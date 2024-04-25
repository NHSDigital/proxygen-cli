import pathlib
import json
from typing import Optional
import yaml
import sys
import os

import click
from pydantic import (
    BaseSettings,
    validator,
    AnyHttpUrl,
    ValidationError,
)

from . import dot_proxygen


def _yaml_credentials_file_source(_):
    with dot_proxygen.credentials_file().open() as yaml_file:
        credentials = yaml.safe_load(yaml_file)
        return credentials or {}


def create_yaml_credentials_file():
    file_path = os.path.expanduser("~/.proxygen/credentials.yaml")

    if not os.path.exists(file_path):
        with open(file_path, 'w'):
            pass


class Credentials(BaseSettings):
    base_url: AnyHttpUrl = (
        "https://identity.prod.api.platform.nhs.uk/realms/api-producers"
    )
    private_key_path: Optional[str] = None
    key_id: Optional[str] = None
    client_id: str
    client_secret: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    @validator("username", "password", "client_secret", "client_id")
    def validate_humans_users(cls, value, values):
        if values.get("private_key_path") is None and value is None:
            raise ValueError("field required")
        return value

    def private_key(self):
        """read the private key file and self.private_key_file_path."""
        private_key_file = dot_proxygen.directory().joinpath(self.private_key_path)
        if not private_key_file.exists():
            raise ValueError(
                f"Could not open private key file {private_key_file} for machine user {self.name}"
            )
        with private_key_file.open() as f:
            return f.read()

    @validator("key_id")
    def validate_kid(cls, kid, values):
        """
        If authenticating using a machine (with an associated jwks configured in Keycloak) key,
        then the key id is required for newer versions of Keycloak.
        """
        if values.get("private_key_path") and not kid:
            raise ValueError("Private key specified with no associated Key ID (KID)")
        return kid

    @validator("private_key_path")
    def validate_private_key_path(cls, private_key_path):
        """
        Pydantic only allows relative to cwd with FilePath.
        So take string.
        """
        return cls._validate_private_key_path(private_key_path)

    @staticmethod
    def _validate_private_key_path(private_key_path):
        """
        Patchable version of the private key path validator logic.
        """
        if not private_key_path:
            return
        private_key_path = pathlib.Path(private_key_path)
        if private_key_path.is_absolute():
            private_key_file = private_key_path
        else:
            private_key_file = dot_proxygen.directory().joinpath(private_key_path)

        if not private_key_file.exists():
            raise ValueError(f"{private_key_file} does not exist")
        if private_key_file.is_dir():
            raise ValueError(f"{private_key_path} is a directory, not a file")
        return str(private_key_file)

    class Config:
        env_prefix = "PROXYGEN_CREDENTIALS_"
        case_sensitive = True

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                env_settings,
                _yaml_credentials_file_source,
            )


_CREDENTIALS = None
def initialise_credentials():
    global _CREDENTIALS
    try:
        _CREDENTIALS = Credentials()
    except ValidationError as e:
        errors = json.loads(e.json())
        print("*" * 100, file=sys.stderr)
        print(
            "Warning: Credentials invalid or not configured. See `proxygen credentials`.",
            file=sys.stderr,
        )
        details = "  " + "\n  ".join(
            f"{error['loc'][0]}: {error['msg']}" for error in errors
        )
        print(details, file=sys.stderr)
        print("*" * 100, file=sys.stderr)
        _CREDENTIALS = None


def get_credentials():
    initialise_credentials()
    global _CREDENTIALS
    return _CREDENTIALS
