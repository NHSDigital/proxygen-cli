from unittest.mock import patch

from click.testing import CliRunner

from proxygen_cli.cli.command_settings import list
from proxygen_cli.lib.settings import Settings


def test_list_settings(update_config):

    mock_settings = "\n".join([
        "api: proxygen-cli-pytest",
        "endpoint_url: https://mock-proxygen.nhs.uk",
        "spec_output_format: json",
    ])

    update_config(settings=mock_settings)

    with patch("proxygen_cli.cli.command_settings.SETTINGS",  Settings()):
        runner = CliRunner()
        result = runner.invoke(list)

    assert result.output.strip() == mock_settings
