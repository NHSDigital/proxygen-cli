import pytest
from click.testing import CliRunner
from command_main_test import main, CLI_VERSION

def test_version_command():
    """
    Test the version command to ensure it returns the correct version.
    """
    runner = CliRunner()
    result = runner.invoke(main, ["version"])
    assert result.exit_code == 0  # Ensure the command runs successfully
    assert f"proxygen CLI, version {CLI_VERSION}" in result.output  # Check the correct version in the output
