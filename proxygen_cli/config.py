from typing import Dict, Literal, List, Optional, Tuple
from functools import lru_cache
from configparser import ConfigParser
from pydantic import BaseModel, BaseSettings, validator, root_validator, AnyUrl
from pydantic.env_settings import SettingsSourceCallable

from . import dot_proxygen
from .credentials import CREDENTIALS


class ApiConfig(BaseModel):
    name: Optional[str] = None
    client: str = None
    user: str = None
    machine_user: str = None
    endpoint_url: AnyUrl = "https://proxygen.ptl.api.platform.nhs.uk"
    output: Literal["json", "yaml"] = "yaml"

    @root_validator()
    def only_user_or_machine(cls, values):
        user = values.get("user")
        machine_user = values.get("machine_user")
        if (user and machine_user):
            config_file = dot_proxygen.config_file()
            error_msg = f"Invalid config for [{values['api']}] in {config_file}. Please choose one of user/machine_user."
            raise ValueError(error_msg)
        return values

    @validator("client", always=True)
    def validate_client(cls, client_id, values):
        client_ids = [c.id for c in CREDENTIALS.clients]
        if client_id is None and len(client_ids) == 1:
            return client_ids[0]
        elif client_id is None:
            raise ValueError(f"Client not specified, but mutiple available: {client_ids}. Please configure api {values['name']}. (This value should be this the client_id).")
        elif client_id in client_ids:
            return client_id
        else:
            raise ValueError(f"No credentials matching client '{client_id}'. (This value should be this the client_id).")
        return client_id
        
    @validator("user", "machine_user", always=True)
    def validate_user(cls, username, values, field):
        if field.name == "user":
            usernames = [user.name for user in CREDENTIALS.users]
        else:
            usernames = [user.name for user in CREDENTIALS.machine_users]
        if username is None and len(usernames) == 1:
            return usernames[0]
        if username is not None and username not in usernames:
            raise ValueError(f"No credentials matching user '{username}'.")
        return username


class _ConfigFile(BaseSettings):
    apis: Dict[str, ApiConfig]
    
    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return init_settings, _config_file_settings


def _config_file_settings(config_file: _ConfigFile):
    config_file_name = str(dot_proxygen.config_file())
    config_file = ConfigParser(default_section="default")
    config_file.read(config_file_name)

    configs = {"apis": {}}
    for api_name in config_file.sections():
        configs["apis"][api_name] = {k: v for k, v in config_file.items(api_name)}
        configs["apis"][api_name]["name"] = api_name
    return configs


CONFIG = _ConfigFile()
DEFAULT_CONFIG = None


def set_api_config(api_name: Optional[str], default: bool=True, **kwargs):
    if api_name not in CONFIG.apis:
        CONFIG.apis[api_name] = ApiConfig(name=api_name, **kwargs)
    else: # Update
        defaults = CONFIG.apis[api_name].dict()
        defaults.update(kwargs)
        CONFIG.apis[api_name] = ApiConfig(**defaults)

    if default:
        global DEFAULT_CONFIG
        DEFAULT_CONFIG = api_name

    return CONFIG.apis[api_name]


def get(api_name: str = None):
    if api_name is None:
        api_name = DEFAULT_CONFIG
    return CONFIG.apis[api_name]
