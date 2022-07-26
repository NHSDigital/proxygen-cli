import requests
import uuid
import time
import jwt
from configparser import ConfigParser
from os.path import exists
from pathlib import Path
import click



_SESSION = requests.session()
AUTH_URL = "https://identity.ptl.api.platform.nhs.uk/auth/realms/api-producers/protocol/openid-connect/auth"
ACCESS_TOKEN_URL = "https://identity.ptl.api.platform.nhs.uk/auth/realms/api-producers/protocol/openid-connect/token"

PAAS_CREDENTIAL_FILE = Path.home() / ".paasrc"

MIN_TOKEN_TIME_REMAINING_SECS = 10


def update_auth_config_file(config):
  with open(PAAS_CREDENTIAL_FILE, "w") as f:
    config.write(f)

def generate_client():
  return requests.session(headers={"Authorization": f"Bearer {_get_token()}"})

def _get_token():
  config = get_auth_config()
  if not config._sections.get("token") or config.get("token","expires") + MIN_TOKEN_TIME_REMAINING_SECS <= time():
    _refresh_paas_token(config)
    update_auth_config_file(config)

  return config["token"]["access_token"]


def _load_private_key(private_key_file):
  with open(private_key_file, "r") as f:
    return f.read()



def _refresh_paas_token(config):
  cred = config._sections.get("credentials")
  grant_type = cred["grant_type"]
  username = cred.get("username")
  client_id = cred.get("client_id")
  client_secret = cred.get("client_secret")
  private_key_file = cred.get("private_key_file")

  if grant_type == "paasword":
    headers = {"username": username, "password": _prompt_password(), "grant_type": "password", "client_id": client_id }
  elif grant_type == "client_credentials":
    headers = {"grant_type": "client_credentials", "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer", 
               "client_assertion": _generate_client_assertion(client_id, _load_private_key(private_key_file)),}
  else:
    raise Exception(f"Invalid credential file {PAAS_CREDENTIAL_FILE}")

  resp = _SESSION.post(ACCESS_TOKEN_URL, data=headers)
  resp.raise_for_status()
  token_data = resp.json()
  token_data["expires"] = time() + token_data["expires_in"]
  config["token"] = token_data

def _generate_client_assertion(client_id, private_key):
  claims = {
    "sub": client_id,
        "iss": client_id,
        "jti": str(uuid.uuid4()),
        "aud": ACCESS_TOKEN_URL,
        "exp": int(time()) + 300,  # 5mins in the future
  }
  return jwt.encode(claims, private_key, algorithm="RS512")