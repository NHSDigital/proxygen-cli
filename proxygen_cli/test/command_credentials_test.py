from unittest.mock import patch

import yaml
import pytest
from click.testing import CliRunner
from pydantic.error_wrappers import ValidationError

import proxygen_cli.cli.command_credentials as cmd_credentials
from proxygen_cli.lib.credentials import Credentials


def get_test_credentials(**kwargs):
    base_credentials = {
        "base_url": "https://mock-keycloak-url.nhs.uk",
        "client_id": "mock-api-client",
        "client_secret": "1a2f4g5",
        "password": "mock-password",
        "username": "mock-user",
    }

    updated_credentials = base_credentials | kwargs

    text_format_credentials = [
        f"{key}: {value}" for key, value in updated_credentials.items()
    ]

    return "\n".join(text_format_credentials)


def test_missing_credentials(update_config):
    mock_credentials = get_test_credentials(username="")
    update_config(credentials=mock_credentials)

    with pytest.raises(ValidationError):
        Credentials()


def test_list_credentials(patch_config):
    mock_credentials = get_test_credentials()

    with patch_config(credentials=mock_credentials):
        runner = CliRunner()
        result = runner.invoke(cmd_credentials.list)

    assert result.output.strip() == mock_credentials


def test_get_credential(patch_config):
    mock_credentials = get_test_credentials()

    with patch_config(credentials=mock_credentials):
        runner = CliRunner()
        result = runner.invoke(cmd_credentials.get, ["client_id"])

    assert result.output.strip() == "mock-api-client"


def test_get_invalid_setting(patch_config):
    mock_credentials = get_test_credentials()

    with patch_config(credentials=mock_credentials):
        runner = CliRunner()
        result = runner.invoke(cmd_credentials.get, ["invalid"])

        assert "'invalid' is not one of 'base_url'" in result.output.strip()


def test_private_key_id_missing(patch_config):
    """
    Ensure that if the private_key_path is set, then we validate key_id.
    We mock out the file path validation using an extra patch as we're already
    mocking part of Credentials with the patch_config mark.
    """
    mock_credentials = get_test_credentials()

    with patch_config(credentials=mock_credentials), \
            patch(("proxygen_cli.lib.credentials.Credentials."
                   "_validate_private_key_path")) as mock_creds:
        mock_creds.return_value = True
        runner = CliRunner()
        result = runner.invoke(
            cmd_credentials.set,
            ["private_key_path", "not_a_valid_file"]
        )

        assert "Private key specified with no associated Key ID" in \
            result.output.strip()


def test_set_credential(patch_config, credentials_file):
    mock_credentials = get_test_credentials()

    with patch_config(credentials=mock_credentials):
        runner = CliRunner()
        runner.invoke(cmd_credentials.set, ["username", "new-username"])

    expected_credentials = "\n".join(
        [
            "base_url: https://mock-keycloak-url.nhs.uk",
            "client_id: mock-api-client",
            "client_secret: 1a2f4g5",
            "password: mock-password",
            "username: new-username",
        ]
    )

    # Check the file has been written to
    assert credentials_file() == expected_credentials


def test_update_credentials(patch_config, credentials_file):
    mock_credentials = get_test_credentials()

    # Convert mock_credentials to a dictionary
    mock_credentials_dict = yaml.safe_load(mock_credentials)

    # Set an initial value for the username field
    initial_username = "old-username"
    mock_credentials_dict["username"] = initial_username

    with patch_config(credentials=mock_credentials):
        runner = CliRunner()
        runner.invoke(cmd_credentials.set, ["username", "new-username123"])

    expected_credentials = "\n".join(
        [
            "base_url: https://mock-keycloak-url.nhs.uk",
            "client_id: mock-api-client",
            "client_secret: 1a2f4g5",
            "password: mock-password",
            "username: new-username123",  # Updated value
        ]
    )

    # Check the file has been written to
    assert credentials_file() == expected_credentials


def test_add_key_id(patch_config, credentials_file):
    mock_credentials = get_test_credentials()

    with patch_config(credentials=mock_credentials):
        runner = CliRunner()
        runner.invoke(cmd_credentials.set, ["key_id", "test_kid"])

    expected_credentials = "\n".join(
        [
            "base_url: https://mock-keycloak-url.nhs.uk",
            "client_id: mock-api-client",
            "client_secret: 1a2f4g5",
            "key_id: test_kid",
            "password: mock-password",
            "username: mock-user",
        ]
    )

    # Check the file has been written to
    assert credentials_file() == expected_credentials


def test_set_invalid_setting(patch_config):
    mock_credentials = get_test_credentials()
    with patch_config(credentials=mock_credentials):
        runner = CliRunner()
        result = runner.invoke(cmd_credentials.set, ["invalid", "new-username"])

    assert "Error: Invalid value: extra fields not permitted" in result.output.strip()


def test_set_invalid_private_key_path(patch_config):
    mock_credentials = get_test_credentials()
    with patch_config(credentials=mock_credentials):
        runner = CliRunner()
        result = runner.invoke(
            cmd_credentials.set, ["private_key_path", "invalid_private_key_path"]
        )

    assert ".proxygen/invalid_private_key_path does not exist" in result.output.strip()


def test_remove_setting(patch_config, credentials_file):
    mock_credentials = get_test_credentials()

    with patch_config(credentials=mock_credentials):
        runner = CliRunner()
        runner.invoke(cmd_credentials.rm, ["private_key_path"])

    expected_credentials = "\n".join(
        [
            "base_url: https://mock-keycloak-url.nhs.uk",
            "client_id: mock-api-client",
            "client_secret: 1a2f4g5",
            "password: mock-password",
            "username: mock-user",
        ]
    )

    # Check the file has been written to
    assert credentials_file() == expected_credentials


def test_remove_invalid_setting(patch_config):
    mock_credentials = get_test_credentials()

    with patch_config(credentials=mock_credentials):
        runner = CliRunner()
        result = runner.invoke(cmd_credentials.rm, ["invalid"])

        assert "'invalid' is not one of 'base_url'" in result.output.strip()
