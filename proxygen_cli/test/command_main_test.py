import json
from unittest.mock import patch
from click.testing import CliRunner
from proxygen_cli.cli.command_main import status, main  # Import `main` for the version test
from proxygen_cli.lib.settings import Settings
from proxygen_cli.test.command_settings_test import get_test_settings


def test_proxygen_status(patch_config, patch_request):
    runner = CliRunner()

    mock_settings = get_test_settings(
        endpoint_url="https://mock-proxygen.nhs.uk",
    )

    with patch_config(settings=mock_settings, path="cli.command_main"), patch_request(
        200, {"mock_return": "value"}
    ):
        result = runner.invoke(status)

    assert json.loads(result.output) == {
        "proxygen_url": "https://mock-proxygen.nhs.uk",
        "response": {"mock_return": "value"},
    }

def test_main_version():
    runner = CliRunner()
    result = runner.invoke(main, ['--version'])  # Correctly invoke the main CLI group
    assert result.exit_code == 0
    version_output = result.output.strip()  # Clean up the output by stripping whitespace

    # Print the version output to the console
    print(f"Version Output: {version_output}")  # This will print the version during the test

    # Assert that the output contains the version information automatically provided by Click
    assert "proxygen, version" in version_output  # This works as Click handles versioning
