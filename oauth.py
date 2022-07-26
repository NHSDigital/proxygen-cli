import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient
import uuid
from time import time
import jwt
from oauthlib.oauth2 import TokenExpiredError

# Dependent on environment
def _redirect_uri(base): return f"{base}/callback"
def _auth_url(base): return f"{base}/auth/realms/api-producers/protocol/openid-connect/auth"
def _access_token_url(base): return f"{base}/auth/realms/api-producers/protocol/openid-connect/token"
def _aud_url(base): return f"{base}/auth/realms/api-producers"

SCOPE = ["openid"]

def get_authenticated_client_token(*, client_id, client_secret, base_url, username=None, private_key=None, get_password=None, token=None):

  def token_saver(_token):
    token = _token

  if token and token["expires_at"] >= time() + 5:
    # Try refresh token login flow first
    try:
      oauth = OAuth2Session(client_id, token=token, auto_refresh_url=_access_token_url(base_url),
                                scope=SCOPE, token_updater=token_saver)
    except TokenExpiredError:
      pass
    else:
      return oauth.token, oauth

  if username and get_password:
    # User login flow
    client = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
    token = client.fetch_token(token_url=_access_token_url(base_url),
            username=username, password=get_password(), client_id=client_id,
            client_secret=client_secret)

  elif private_key:
    # Machine user login flow
    claims = {
            "sub": client_id,
            "iss": client_id,
            "jti": str(uuid.uuid4()),
            "aud": _aud_url(base_url),
            "exp": int(time()) + 300,
    }
    with open(private_key, "r") as f:
            private_key = f.read()

    client_assertion = jwt.encode(claims, private_key, algorithm="RS512")
    token_response = requests.post(
        _access_token_url(base_url),
        data={
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": client_assertion,
        },
    )
    assert token_response.status_code == 200
    client = requests.session()
    client.headers.update({"Authorization": f"Bearer {token_response.json()['access_token']}"})
    token = token_response.json()
    token["expires_in"] = int(time()) + 300

  else:

    raise RuntimeError("Must provide username and fetch password or")

  return token, client
