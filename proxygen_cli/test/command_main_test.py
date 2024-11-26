import json
from unittest.mock import patch

from click.testing import CliRunner

from proxygen_cli.cli.command_main import status, main  # Import main instead of version
from proxygen_cli.lib.settings import Settings
from proxygen_cli.test.command_settings_test import get_test_settings


def test_proxygen_status(patch_config, patch_request):
    """
    Test the `status` command of the proxygen CLI.
    It mocks the settings and API response to validate the output.
    """
    runner = CliRunner()

    mock_settings = get_test_settings(
        endpoint_url="https://mock-proxygen.nhs.uk",
    )

    with patch_config(settings=mock_settings, path="cli.command_main"), patch_request(
        200, {"mock_return": "value"}
    ):
        result = runner.invoke(status)

    # Assert that the output matches the mocked response
    assert json.loads(result.output) == {
        "proxygen_url": "https://mock-proxygen.nhs.uk",
        "response": {"mock_return": "value"},
    }


def test_proxygen_version():
    """
    Test the `version` command of the proxygen CLI.
    It mocks the `get_version` function to avoid dependency on pyproject.toml.
    """
    runner = CliRunner()

    # Mock the version function to return a fixed value
    with patch("proxygen_cli.cli.command_main.get_version", return_value="2.1.18"):
        result = runner.invoke(main, ['version'])  # Correct invocation of version command via main

    # Assert that the command runs successfully and outputs the correct version
    assert result.exit_code == 0
    assert result.output.strip() == "proxygen, version 2.1.18"
