from typing import Literal
from pydantic import BaseSettings, AnyUrl

import yaml

from .dot_proxygen import settings_file


def _yaml_settings_file_source(_):
    with settings_file().open() as yaml_file:
        settings = yaml.safe_load(yaml_file)
        return settings or {}


class Settings(BaseSettings):
    endpoint_url: AnyUrl = "https://proxygen.prod.api.platform.nhs.uk"
    spec_output_format: Literal["json", "yaml"] = "yaml"
    api: str = None

    class Config:
        env_prefix = "PROXYGEN_CREDENTIALS_"

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
                _yaml_settings_file_source,
            )


SETTINGS = Settings()
