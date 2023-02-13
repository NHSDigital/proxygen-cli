import json
import pathlib
import sys
from typing import Optional

import click
import yaml
from pydantic import AnyHttpUrl, BaseSettings, ValidationError, validator

from . import dot_proxygen


def _yaml_credentials_file_source(_):
    with dot_proxygen.credentials_file().open() as yaml_file:
        credentials = yaml.safe_load(yaml_file)
        return credentials or {}


class Credentials(BaseSettings):
    base_url: AnyHttpUrl = AnyHttpUrl(
        "https://identity.prod.api.platform.nhs.uk/auth/realms/api-producers", scheme="https"
    )
    private_key_path: Optional[str] = None
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
            raise ValueError(f"Could not open private key file {private_key_file} for machine user {self.name}")
        with private_key_file.open() as f:
            return f.read()

    @validator("private_key_path")
    def validate_private_key_path(cls, private_key_path):
        """
        Pydantic only allows relative to cwd with FilePath.
        So take string.
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
            _,
        ):
            return (
                init_settings,
                env_settings,
                _yaml_credentials_file_source,
            )


_CREDENTIALS = None
try:
    _CREDENTIALS = Credentials()
except ValidationError as e:
    errors = json.loads(e.json())
    print("*" * 100, file=sys.stderr)
    print(
        "Warning: Credentials invalid or not configured. See `proxygen credentials`.",
        file=sys.stderr,
    )
    DETAILS = "  " + "\n  ".join(f"{error['loc'][0]}: {error['msg']}" for error in errors)
    print(DETAILS, file=sys.stderr)
    print("*" * 100, file=sys.stderr)
    _CREDENTIALS = None


def get_credentials():
    if _CREDENTIALS is None:
        raise click.UsageError("This command requires credentials which are invalid or not configured")
    return _CREDENTIALS
