from typing import Optional, Literal, List, Tuple
from functools import lru_cache
from configparser import ConfigParser
import pathlib
import json
import hashlib

from pydantic import BaseModel, BaseSettings, FilePath, validator
from pydantic.env_settings import SettingsSourceCallable

from . import dot_proxygen


class ClientCredentials(BaseModel):
    id: str
    secret: str
    base_url: Optional[str] = None


class UserCredentials(BaseModel):
    name: str
    password: str


class MachineUserCredentials(BaseModel):
    name: str
    private_key_path: str

    @validator("private_key_path")
    def validate_private_key_path(cls, private_key_path):
        """
        Pydantic only allows relative to cwd with FilePath.
        So take string.
        """
        private_key_path= pathlib.Path(private_key_path)
        if private_key_path.is_absolute():
            private_key_file = private_key_path
        else:
            private_key_file = dot_proxygen.credentials_file().parent.joinpath(private_key_path)

        if not private_key_file.exists():
            raise ValueError(f"{private_key_file} does not exist")
        if private_key_file.is_dir():
            raise ValueError(f"{private_key_path} is a directory, not a file")
        return private_key_file
    
    
    def private_key(self):
        private_key_file = dot_proxygen.credentials_file().joinpath(
            self.private_key_path
        )
        if not private_key_file.exists():
            raise ValueError(
                f"Could not open private key file {private_key_file} for machine user {self.name}"
            )
        with private_key_file.open() as f:
            return f.read()



class CredentialsFile(BaseSettings):
    clients: List[ClientCredentials]
    users: List[UserCredentials]
    machine_users: List[MachineUserCredentials]

    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return init_settings, credentials_file_settings

def credentials_file_settings(CredentialsFile: CredentialsFile):
    credentials_file_name = str(dot_proxygen.credentials_file())
    credentials_file = ConfigParser(default_section="default")
    credentials_file.read(credentials_file_name)

    values = {
        "clients": [],
        "users": [],
        "machine_users": [],
    }

    allowed_prefixes = [k[:-1] for k in list(values.keys())]
    for section in credentials_file.sections():
        section_prefix, section_name = section.split(" ", 1)
        if section_prefix not in allowed_prefixes:
            raise ValueError(
                f"Invalid section header {section}, should start with one of {allowed_prefixes}"
            )
        item = {k: v for k,v in credentials_file.items(section)}
        if section_prefix == "client":
            item["id"] = section_name
        else:
            item["name"] = section_name
        values[section_prefix + "s"].append(item)
    return values


CREDENTIALS = CredentialsFile()

def get_client(client_id):
    return next(filter(lambda client: client.id == client_id, CREDENTIALS.clients))

def get_user(username):
    return next(filter(lambda user: user.name == username, CREDENTIALS.users + CREDENTIALS.machine_users))
