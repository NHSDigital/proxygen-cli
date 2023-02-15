from unittest.mock import patch

import pytest

from proxygen_cli.lib.settings import Settings


@pytest.fixture(autouse=True, name="default_config")
def default_config_files_fixture(tmp_path):
    # tmp_path fixture creates a new directory in tmp/
    # this is done for every test as it's inexpensive and allows test independence

    # Recreate the proxygen config directory structure
    dot_proxygen_dir = tmp_path / ".proxygen"
    dot_proxygen_dir.mkdir()
    settings = dot_proxygen_dir / "settings.yaml"
    credentials = dot_proxygen_dir / "credentials.yaml"
    credentials.touch()

    # Add some default settings
    default_settings = "\n".join([
        "api: hello-world",
        "endpoint_url: https://proxygen.prod.api.platform.nhs.uk",
        "spec_output_format: yaml"
    ])
    settings.write_text(default_settings)

    # Add some default credentials
    default_credentials = "\n".join([

    ])
    credentials.write_text(default_credentials)

    # Patch the directory function which tells the cli where to look for the config files
    with patch("proxygen_cli.lib.dot_proxygen.directory") as _dir:
        _dir.return_value = dot_proxygen_dir

        # Patch the settings object everywhere it's called
        mocked_settings = Settings()
        with (
            patch("proxygen_cli.cli.command_settings.SETTINGS",  mocked_settings),
            patch("proxygen_cli.cli.command_docker.SETTINGS",  mocked_settings),
            patch("proxygen_cli.cli.command_instance.SETTINGS",  mocked_settings),
            patch("proxygen_cli.cli.command_main.SETTINGS",  mocked_settings),
            patch("proxygen_cli.cli.command_secret.SETTINGS",  mocked_settings),
            patch("proxygen_cli.cli.command_spec.SETTINGS",  mocked_settings),
            patch("proxygen_cli.lib.output.SETTINGS",  mocked_settings),
            patch("proxygen_cli.lib.proxygen_api.SETTINGS",  mocked_settings),
            patch("proxygen_cli.lib.settings.SETTINGS",  mocked_settings),
            patch("proxygen_cli.lib.spec_server.SETTINGS",  mocked_settings),

        ):
            yield settings, credentials


@ pytest.fixture(name="update_config")
def overwrite_default_config(default_config):
    """
    Overwrite default settings on a per test basis.
    Will then need to patch a re-initialized settings object in the test case.
    See command_settings_test.test_list for usage
    """
    settings_file, credentials_file = default_config

    def overwrite_func(settings=None, credentials=None):
        if settings:
            settings_file.write_text(settings)
        if credentials:
            credentials_file.write_text(credentials)

        return settings_file, credentials_file

    yield overwrite_func
