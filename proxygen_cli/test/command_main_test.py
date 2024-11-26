import json
from unittest.mock import patch
from click.testing import CliRunner
from proxygen_cli.cli.command_main import status, main  # Import main instead of version
from proxygen_cli.lib.settings import Settings
from proxygen_cli.test.command_settings_test import get_test_settings
import subprocess

def get_current_version():
    """
    Function to get the current version of the proxygen package dynamically.
    This assumes the version is accessible via a command like `proxygen --version`.
    """
    result = subprocess.run(
        ["proxygen", "version"], capture_output=True, text=True
    )
    # Extract only the version number by splitting the output
    return result.stdout.strip().split("version")[-1].strip()

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
    It fetches the current version dynamically and tests it against the output.
    """
    runner = CliRunner()

    # Get the current version dynamically
    current_version = get_current_version()
    print(f"Current version: {current_version}")  # Optional: Print to verify the fetched version

    # Run the version command
    result = runner.invoke(main, ['version'])  # Correct invocation of version command via main

    # Assert that the command runs successfully and outputs the correct version
    assert result.exit_code == 0
    assert result.output.strip() == f"proxygen, version {current_version}"
