import json
from unittest.mock import patch

from click.testing import CliRunner

from proxygen_cli.cli.command_main import status
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
