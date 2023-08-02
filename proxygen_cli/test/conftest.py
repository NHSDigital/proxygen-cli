from contextlib import contextmanager
from unittest.mock import Mock, patch

import pytest

from proxygen_cli.lib.credentials import Credentials
from proxygen_cli.lib.settings import Settings
from proxygen_cli.test.mock_private_key import MOCK_PRIVATE_KEY


@pytest.fixture(name="default_config")
def default_config_files_fixture(tmp_path):
    # tmp_path fixture creates a new directory in tmp/
    # this is done for every test as it's inexpensive and allows test independence

    # Recreate the proxygen config directory structure
    dot_proxygen_dir = tmp_path / ".proxygen"
    dot_proxygen_dir.mkdir()
    settings = dot_proxygen_dir / "settings.yaml"
    credentials = dot_proxygen_dir / "credentials.yaml"
    private_key_dir = dot_proxygen_dir / "path_to"
    private_key_dir.mkdir()
    private_key = private_key_dir / "private_key.pem"

    # Add some default settings
    default_settings = "\n".join(
        [
            "api: hello-world",
            "endpoint_url: https://proxygen.prod.api.platform.nhs.uk",
            "spec_output_format: yaml",
        ]
    )
    settings.write_text(default_settings)

    # Add some default credentials
    default_credentials = "\n".join(
        [
            "client_id: hello-world-client",
            "client_secret: 12345",
            "private_key_path: private_key_path.pem",
            "username: deathstar",
            "password: mock-password",
        ]
    )
    credentials.write_text(default_credentials)

    # Add a made up private key
    private_key.write_text(MOCK_PRIVATE_KEY)

    # Patch the directory function which tells the cli where to look for the config files
    with patch("proxygen_cli.lib.dot_proxygen.directory") as _dir:
        _dir.return_value = dot_proxygen_dir
        yield settings, credentials


@pytest.fixture(name="update_config")
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


@pytest.fixture(name="settings_file")
def settings_file_fixture(default_config):
    """Yields a function that returns the up to date contents of the settings file created in the temp dir"""
    settings_file, _ = default_config

    def read_settings_file():
        with open(settings_file, "r", encoding="utf-8") as f:
            return f.read().strip()

    yield read_settings_file


@pytest.fixture(name="credentials_file")
def credentials_file_fixture(default_config):
    """Yields a function that returns the up to date contents of the credentials file created in the temp dir"""
    _, credentials_file = default_config

    def read_credentials_file():
        with open(credentials_file, "r", encoding="utf-8") as f:
            return f.read().strip()

    yield read_credentials_file


@pytest.fixture(name="mock_response")
def mock_response_fixture():
    class MockResponse:
        def __init__(self, text, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.text = text

        def json(self):
            return self.json_data

    yield MockResponse


@pytest.fixture(name="patch_pathlib")
def patch_pathlib_fixture():
    """Yields a function that patches pathlib with an object that can be treated like a file"""

    def patch_pathlib(file_contents):
        class MockFileContents:
            def read(self):
                return file_contents

        class MockFile:
            def __init__(self, *_):
                pass

            @staticmethod
            def exists():
                return True

            @contextmanager
            def open(_):
                return (x for x in [MockFileContents()])

            @staticmethod
            def is_dir():
                return False

            def __call__(self, *_):
                return self

        return patch(
            "proxygen_cli.lib.spec.pathlib.Path",
            MockFile("test-yaml-key: test-yaml-value"),
        )

    yield patch_pathlib


@pytest.fixture(name="patch_request")
def patch_request_fixture(mock_response):
    """Yields a function that returns a patch of the proxygen cli request function"""

    def patched_request_func(status, response, _type="text"):
        response = Mock(return_value=mock_response(_type, response, status))
        return patch("proxygen_cli.lib.proxygen_api.requests.Session.request", response)

    yield patched_request_func


@pytest.fixture(name="patch_spec_resolver")
def patch_spec_resolver_fixture():
    """
    Yields a function that returns a patch of the proxygen spec resolver which
    skips validation and returns an empty spec dictionary.
    """

    def patched_spec_resolver_func():
        return patch("proxygen_cli.lib.spec.resolve", Mock(return_value={}))

    yield patched_spec_resolver_func

@pytest.fixture(name="patch_click_confirm")
def patch_click_confirm_fixture():
    """Mocks out the click.confirm() method to always return True"""

    def patched_click_confirm_func():
        return patch("click.confirm", return_value=True)

    yield patched_click_confirm_func

@pytest.fixture(name="patch_access_token")
def patch_access_token_fixture():
    """Yields a function that returns a patch of the proxygen cli access_token function"""

    def patched_access_token_func(return_value="12345"):
        return patch(
            "proxygen_cli.lib.proxygen_api.access_token",
            Mock(return_value=return_value),
        )

    yield patched_access_token_func


@pytest.fixture(name="patch_config")
def patch_config_fixture(default_config):
    """Yields a functions that returns a patch of settings from the passed module"""

    settings_file, credentials_file = default_config

    def patched_settings_func(settings=None, credentials=None, path=None):
        if settings:
            patch_path = path or "cli.command_settings"
            settings_file.write_text(settings)
            return patch(f"proxygen_cli.{patch_path}.SETTINGS", Settings())

        else:
            patch_path = path or "lib.credentials"
            credentials_file.write_text(credentials)
            return patch("proxygen_cli.lib.credentials._CREDENTIALS", Credentials())

    yield patched_settings_func
