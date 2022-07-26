from functools import partial
from pathlib import Path
import json
from typing import Literal, Optional, Union
from pydantic import BaseModel, Field, validator, FilePath
import click
from typing_extensions import Annotated


from oauth import get_authenticated_client_token

# Dependent on environment

# Customizable
PAAS_CREDENTIAL_FILE = Path.home() / ".paasrc"
username = ""
password = ""
key = "/home/domplatypus/tmp/proxygen-test-keys/jwtRS512.key"


client_id = "test-signed-jwt"

class MachineAuth(BaseModel):

  auth_type: Literal["machine"] = "machine"
  client_id: str
  base_url: str
  private_key: FilePath
  token: Optional[dict]

class UserAuth(BaseModel):

  auth_type: Literal["user"] = "user"
  client_id: str
  client_secret: str
  base_url: str
  username: str
  token: Optional[dict]

AuthConfig = Annotated[Union[UserAuth, MachineAuth], Field(discriminator="auth_type")]


def _prompt_password(user):
    return click.prompt(f"Please input password for user {user}", type=str, hide_input=True)


def get_config() -> AuthConfig:
  if not PAAS_CREDENTIAL_FILE:
    PAAS_CREDENTIAL_FILE.touch()

  try:
    with open(PAAS_CREDENTIAL_FILE, 'r') as f:
      config = json.load(f)
  except:
    raise RuntimeError(f"Check {PAAS_CREDENTIAL_FILE}")

  return config

def update_config(config: AuthConfig):
  with open(PAAS_CREDENTIAL_FILE, 'w') as f:
    json.dump(config.json(), f, indent=4)


def get_cached_client():
  config = get_config()
  token, client = get_authenticated_client_token(
    **config, get_password=partial(_prompt_password, config.get("username"))
  )

  config["token"] = token
  update_config(config)

  return client
