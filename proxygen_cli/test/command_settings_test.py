from unittest.mock import patch

import pytest
from click.testing import CliRunner
from pydantic.error_wrappers import ValidationError

import proxygen_cli.cli.command_settings as cmd_settings
from proxygen_cli.lib.settings import Settings


def get_test_settings(**kwargs):
    base_settings = {
        "api": "proxygen-cli-pytest",
        "endpoint_url": "https://mock-proxygen.nhs.uk",
        "spec_output_format": "json",
    }

    updated_settings = base_settings | kwargs

    text_format_settings = [
        f"{key}: {value}" for key, value in updated_settings.items()
    ]

    return "\n".join(text_format_settings)


def test_list_settings_invalid_url(update_config):
    mock_settings = get_test_settings(endpoint_url="invalid")

    update_config(settings=mock_settings)

    with pytest.raises(ValidationError):
        Settings()


def test_list_settings(patch_config):
    mock_settings = get_test_settings()

    with patch_config(settings=mock_settings):
        runner = CliRunner()
        result = runner.invoke(cmd_settings.list)

    assert result.output.strip() == mock_settings


def test_get_setting(patch_config):
    mock_settings = get_test_settings()

    with patch_config(settings=mock_settings):
        runner = CliRunner()
        result = runner.invoke(cmd_settings.get, ["api"])

    assert result.output.strip() == "proxygen-cli-pytest"


def test_get_invalid_setting(patch_config):
    mock_settings = get_test_settings()

    with patch_config(settings=mock_settings):
        runner = CliRunner()
        result = runner.invoke(cmd_settings.get, ["invalid"])

        assert "'invalid' is not one of 'endpoint_url'" in result.output.strip()


def test_set_setting(patch_config, settings_file):
    mock_settings = get_test_settings()

    with patch_config(settings=mock_settings):
        runner = CliRunner()
        runner.invoke(cmd_settings.set, ["api", "new_api_name"])

    expected_settings = "\n".join(
        [
            "api: new_api_name",
            "endpoint_url: https://mock-proxygen.nhs.uk",
            "spec_output_format: json",
        ]
    )

    assert settings_file() == expected_settings


def test_set_invalid_setting():
    runner = CliRunner()
    result = runner.invoke(cmd_settings.set, ["invalid", "new_api_name"])

    assert "'invalid' is not one of 'endpoint_url'" in result.output.strip()


def test_set_invalid_url():
    runner = CliRunner()
    result = runner.invoke(cmd_settings.set, ["endpoint_url", "invalid_url"])

    assert "invalid or missing URL scheme" in result.output.strip()


def test_remove_setting(patch_config, settings_file):
    mock_settings = get_test_settings()

    with patch_config(settings=mock_settings):
        runner = CliRunner()
        result = runner.invoke(cmd_settings.rm, ["api"])

    expected_settings = "\n".join(
        [
            "endpoint_url: https://mock-proxygen.nhs.uk",
            "spec_output_format: json",
        ]
    )

    # Check the file has been written to
    assert settings_file() == expected_settings

    # Double check that get now returns that value
    with patch("proxygen_cli.cli.command_settings.SETTINGS", Settings()):
        result = runner.invoke(cmd_settings.get, ["api"])

    assert result.output.strip() == ""


def test_remove_invalid_setting(patch_config):
    mock_settings = get_test_settings()

    with patch_config(settings=mock_settings):
        runner = CliRunner()
        result = runner.invoke(cmd_settings.rm, ["invalid"])

        assert " 'invalid' is not one of 'endpoint_url'" in result.output.strip()
