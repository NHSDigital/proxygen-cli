import pathlib

import yaml
from pydantic import BaseSettings, validator, root_validator, AnyHttpUrl

from . import dot_proxygen
    
def _yaml_credentials_file_source(_):
    with dot_proxygen.credentials_file().open() as yaml_file:
        credentials = yaml.safe_load(yaml_file)
        return credentials or {}


class Credentials(BaseSettings):
    base_url: AnyHttpUrl = "https://identity.ptl.api.platform.nhs.uk/auth/realms/api-producers"
    client_id: str
    client_secret: str = None
    username: str = None
    password: str = None
    private_key_path: str = None
    
    def private_key(self):
        """read the private key file and self.private_key_file_path."""
        private_key_file = dot_proxygen.directory().joinpath(self.private_key_path)
        if not private_key_file.exists():
            raise ValueError(
                f"Could not open private key file {private_key_file} for machine user {self.name}"
            )
        with private_key_file.open() as f:
            return f.read()

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
            private_key_file = dot_proxygen.directory().joinpath(private_key_path)

        if not private_key_file.exists():
            raise ValueError(f"{private_key_file} does not exist")
        if private_key_file.is_dir():
            raise ValueError(f"{private_key_path} is a directory, not a file")
        return str(private_key_file)
    
    @root_validator()
    def validate_credentials(cls, credentials):
        if credentials.get("username") is not None and credentials.get("password") is not None:
            return credentials
        elif credentials.get("private_key_path") is not None:
            return credentials
        raise ValueError("Need username/password for human user or private_key_path for machine user.")
    
    class Config:
        env_prefix = "PROXYGEN_CREDENTIALS_"
        case_sensitive=True
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
        
    
CREDENTIALS = Credentials()
