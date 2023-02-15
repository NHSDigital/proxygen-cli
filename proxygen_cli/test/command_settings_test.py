from unittest.mock import patch

import pytest
from click.testing import CliRunner
from pydantic.error_wrappers import ValidationError

import proxygen_cli.cli.command_settings as cmd_settings
from proxygen_cli.lib.settings import Settings


def test_list_settings_invalid_url(update_config):
    mock_settings = "\n".join(
        [
            "api: proxygen-cli-pytest",
            "endpoint_url: invalid",
            "spec_output_format: json",
        ]
    )

    update_config(settings=mock_settings)

    with pytest.raises(ValidationError):
        Settings()


def test_list_settings(update_config):
    mock_settings = "\n".join(
        [
            "api: proxygen-cli-pytest",
            "endpoint_url: https://mock-proxygen.nhs.uk",
            "spec_output_format: json",
        ]
    )

    update_config(settings=mock_settings)

    with patch("proxygen_cli.cli.command_settings.SETTINGS", Settings()):
        runner = CliRunner()
        result = runner.invoke(cmd_settings.list)

    assert result.output.strip() == mock_settings


def test_get_setting(update_config):
    mock_settings = "\n".join(
        [
            "api: proxygen-cli-pytest",
            "endpoint_url: https://mock-proxygen.nhs.uk",
            "spec_output_format: json",
        ]
    )

    update_config(settings=mock_settings)

    with patch("proxygen_cli.cli.command_settings.SETTINGS", Settings()):
        runner = CliRunner()
        result = runner.invoke(cmd_settings.get, ["api"])

    assert result.output.strip() == "proxygen-cli-pytest"


def test_get_invalid_setting(update_config):
    mock_settings = "\n".join(
        [
            "api: proxygen-cli-pytest",
            "endpoint_url: https://mock-proxygen.nhs.uk",
            "spec_output_format: json",
        ]
    )

    update_config(settings=mock_settings)

    with patch("proxygen_cli.cli.command_settings.SETTINGS", Settings()):
        runner = CliRunner()
        result = runner.invoke(cmd_settings.get, ["invalid"])

        expected_error = "\n".join(
            [
                "Usage: get [OPTIONS] {endpoint_url|spec_output_format|api}",
                "Try 'get --help' for help.",
                "",
                "Error: Invalid value for '{endpoint_url|spec_output_format|api}': 'invalid' is not one of 'endpoint_url', 'spec_output_format', 'api'.",
            ]
        )

        assert result.output.strip() == expected_error


def test_set_setting(update_config):
    mock_settings = "\n".join(
        [
            "api: proxygen-cli-pytest",
            "endpoint_url: https://mock-proxygen.nhs.uk",
            "spec_output_format: json",
        ]
    )

    settings_file, _ = update_config(settings=mock_settings)

    with patch("proxygen_cli.cli.command_settings.SETTINGS", Settings()):
        runner = CliRunner()
        runner.invoke(cmd_settings.set, ["api", "new_api_name"])

    expected_settings = "\n".join(
        [
            "api: new_api_name",
            "endpoint_url: https://mock-proxygen.nhs.uk",
            "spec_output_format: json",
        ]
    )

    # Check the file has been written to
    with open(settings_file, "r", encoding="utf-8") as f:
        assert f.read().strip() == expected_settings

    # Double check that get now returns that value
    with patch("proxygen_cli.cli.command_settings.SETTINGS", Settings()):
        result = runner.invoke(cmd_settings.get, ["api"])

    assert result.output.strip() == "new_api_name"


def test_set_invalid_setting():
    runner = CliRunner()
    result = runner.invoke(cmd_settings.set, ["invalid", "new_api_name"])

    expected_error = "\n".join(
        [
            "Usage: set [OPTIONS] {endpoint_url|spec_output_format|api} VALUE",
            "Try 'set --help' for help.",
            "",
            "Error: Invalid value for '{endpoint_url|spec_output_format|api}': 'invalid' is not one of 'endpoint_url', 'spec_output_format', 'api'.",
        ]
    )

    assert result.output.strip() == expected_error


def test_set_invalid_url():
    runner = CliRunner()
    result = runner.invoke(cmd_settings.set, ["endpoint_url", "invalid_url"])

    expected_error = "\n".join(
        [
            "Usage: set [OPTIONS] {endpoint_url|spec_output_format|api} VALUE",
            "Try 'set --help' for help.",
            "",
            "Error: Invalid value: invalid or missing URL scheme",
        ]
    )

    assert result.output.strip() == expected_error


def test_remove_setting(update_config):
    mock_settings = "\n".join(
        [
            "api: proxygen-cli-pytest",
            "endpoint_url: https://mock-proxygen.nhs.uk",
            "spec_output_format: json",
        ]
    )

    settings_file, _ = update_config(settings=mock_settings)

    with patch("proxygen_cli.cli.command_settings.SETTINGS", Settings()):
        runner = CliRunner()
        result = runner.invoke(cmd_settings.rm, ["api"])

    expected_settings = "\n".join(
        [
            "endpoint_url: https://mock-proxygen.nhs.uk",
            "spec_output_format: json",
        ]
    )

    # Check the file has been written to
    with open(settings_file, "r", encoding="utf-8") as f:
        assert f.read().strip() == expected_settings

    # Double check that get now returns that value
    with patch("proxygen_cli.cli.command_settings.SETTINGS", Settings()):
        result = runner.invoke(cmd_settings.get, ["api"])

    assert result.output.strip() == ""


def test_remove_invalid_setting(update_config):
    mock_settings = "\n".join(
        [
            "api: proxygen-cli-pytest",
            "endpoint_url: https://mock-proxygen.nhs.uk",
            "spec_output_format: json",
        ]
    )

    update_config(settings=mock_settings)

    with patch("proxygen_cli.cli.command_settings.SETTINGS", Settings()):
        runner = CliRunner()
        result = runner.invoke(cmd_settings.rm, ["invalid"])

        expected_error = "\n".join(
            [
                "Usage: rm [OPTIONS] {endpoint_url|spec_output_format|api}",
                "Try 'rm --help' for help.",
                "",
                "Error: Invalid value for '{endpoint_url|spec_output_format|api}': 'invalid' is not one of 'endpoint_url', 'spec_output_format', 'api'.",
            ]
        )

        assert result.output.strip() == expected_error
