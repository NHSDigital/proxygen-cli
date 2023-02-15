from unittest.mock import patch

import pytest
from click.testing import CliRunner
from pydantic.error_wrappers import ValidationError

import proxygen_cli.cli.command_credentials as cmd_credentials
from proxygen_cli.lib.credentials import Credentials


def test_missing_credentials(update_config):

    mock_credentials = "\n".join([
        "client_id: mock-api-client",
        "username: mock-user",
        "password: mock-password",
    ])

    update_config(credentials=mock_credentials)

    with pytest.raises(ValidationError):
        Credentials()


def test_list_credentials(update_config):

    mock_credentials = "\n".join([
        "base_url: https://mock-keycloak-url.nhs.uk",
        "client_id: mock-api-client",
        "client_secret: 1a2f4g5",
        "password: mock-password",
        "username: mock-user",
    ])

    update_config(credentials=mock_credentials)

    with patch("proxygen_cli.lib.credentials._CREDENTIALS",  Credentials()):
        runner = CliRunner()
        result = runner.invoke(cmd_credentials.list)

    assert result.output.strip() == mock_credentials

def test_get_credential(update_config):

    mock_credentials = "\n".join([
        "base_url: https://mock-keycloak-url.nhs.uk",
        "client_id: mock-api-client",
        "client_secret: 1a2f4g5",
        "password: mock-password",
        "username: mock-user",
    ])

    update_config(credentials=mock_credentials)

    with patch("proxygen_cli.lib.credentials._CREDENTIALS",  Credentials()):
        runner = CliRunner()
        result = runner.invoke(cmd_credentials.get, ["client_id"])

    assert result.output.strip() == "mock-api-client"

def test_get_invalid_setting(update_config):

    mock_credentials = "\n".join([
        "base_url: https://mock-keycloak-url.nhs.uk",
        "client_id: mock-api-client",
        "client_secret: 1a2f4g5",
        "password: mock-password",
        "username: mock-user",
    ])

    update_config(credentials=mock_credentials)

    with patch("proxygen_cli.lib.credentials._CREDENTIALS",  Credentials()):
        runner = CliRunner()
        result = runner.invoke(cmd_credentials.get, ["invalid"])


        expected_error = "\n".join([
        "Usage: get [OPTIONS]",
        "           {base_url|private_key_path|client_id|client_secret|username|password}",
        "Try 'get --help' for help.",
        "",
        "Error: Invalid value for '{base_url|private_key_path|client_id|client_secret|username|password}': "
        "'invalid' is not one of 'base_url', 'private_key_path', 'client_id', 'client_secret', 'username', 'password'."])

        assert result.output.strip() == expected_error

def test_set_credential(update_config):

    mock_credentials = "\n".join([
        "base_url: https://mock-keycloak-url.nhs.uk",
        "client_id: mock-api-client",
        "client_secret: 1a2f4g5",
        "password: mock-password",
        "username: mock-user",
    ])

    _, credentials_file = update_config(credentials=mock_credentials)

    with patch("proxygen_cli.lib.credentials._CREDENTIALS",  Credentials()):
        runner = CliRunner()
        result = runner.invoke(cmd_credentials.set, ["username", "new-username"])

    expected_credentials = "\n".join([
        "base_url: https://mock-keycloak-url.nhs.uk",
        "client_id: mock-api-client",
        "client_secret: 1a2f4g5",
        "password: mock-password",
        "username: new-username",
    ])

    # Check the file has been written to
    with open(credentials_file, "r", encoding="utf-8") as f:
        assert f.read().strip() == expected_credentials

    # Double check that get now returns that value
    with patch("proxygen_cli.lib.credentials._CREDENTIALS",  Credentials()):
        result = runner.invoke(cmd_credentials.get, ["username"])

    assert result.output.strip() == "new-username"

def test_set_invalid_setting():

    runner = CliRunner()
    result = runner.invoke(cmd_credentials.set, ["invalid", "new-username"])

    expected_error = "\n".join([
        "Usage: set [OPTIONS]",
        "           {base_url|private_key_path|client_id|client_secret|username|password}",
        "           VALUE",
        "Try 'set --help' for help.",
        "",
        "Error: Invalid value for '{base_url|private_key_path|client_id|client_secret|username|password}': "
        "'invalid' is not one of 'base_url', 'private_key_path', 'client_id', 'client_secret', 'username', 'password'."])

    assert result.output.strip() == expected_error

def test_set_invalid_private_key_path():

    runner = CliRunner()
    result = runner.invoke(cmd_credentials.set, ["private_key_path", "invalid_url"])

    expected_error = "\n".join([
        "Invalid private key path"
    ])

    assert result.output.strip() == expected_error




def test_remove_setting(update_config):

    mock_credentials = "\n".join([
        "base_url: https://mock-keycloak-url.nhs.uk",
        "client_id: mock-api-client",
        "client_secret: 1a2f4g5",
        "password: mock-password",
        "username: mock-user",
        "private_key_path: path_to/private_key.pem"
    ])

    _, credentials_file = update_config(credentials=mock_credentials)

    with patch("proxygen_cli.lib.credentials._CREDENTIALS",  Credentials()):
        runner = CliRunner()
        result = runner.invoke(cmd_credentials.rm, ["private_key_path"])

    expected_credentials = "\n".join([
        "base_url: https://mock-keycloak-url.nhs.uk",
        "client_id: mock-api-client",
        "client_secret: 1a2f4g5",
        "password: mock-password",
        "username: mock-user",
    ])

    # Check the file has been written to
    with open(credentials_file, "r", encoding="utf-8") as f:
        assert f.read().strip() == expected_credentials

    # Double check that get now returns that value
    with patch("proxygen_cli.cli.command_settings.SETTINGS",  Credentials()):
        result = runner.invoke(cmd_credentials.get, ["private_key_path"])

    assert result.output.strip() == ""

def test_remove_invalid_setting(update_config):

    mock_credentials = "\n".join([
        "base_url: https://mock-keycloak-url.nhs.uk",
        "client_id: mock-api-client",
        "client_secret: 1a2f4g5",
        "password: mock-password",
        "username: mock-user",
    ])

    update_config(credentials=mock_credentials)

    with patch("proxygen_cli.lib.credentials._CREDENTIALS",  Credentials()):
        runner = CliRunner()
        result = runner.invoke(cmd_credentials.rm, ["invalid"])

        expected_error = "\n".join([
        "Usage: rm [OPTIONS]",
        "          {base_url|private_key_path|client_id|client_secret|username|password}",
        "Try 'rm --help' for help.",
        "",
        "Error: Invalid value for '{base_url|private_key_path|client_id|client_secret|username|password}': "
        "'invalid' is not one of 'base_url', 'private_key_path', 'client_id', 'client_secret', 'username', 'password'."])

        assert result.output.strip() == expected_error
