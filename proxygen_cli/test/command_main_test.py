import json
from unittest.mock import patch

from click.testing import CliRunner

from proxygen_cli.cli.command_main import status
from proxygen_cli.lib.settings import Settings


def test_proxygen_status(update_config, mock_response):
    runner = CliRunner()

    mock_settings = "\n".join(
        [
            "api: proxygen-cli-pytest",
            "endpoint_url: https://mock-proxygen.nhs.uk",
            "spec_output_format: json",
        ]
    )

    update_config(settings=mock_settings)

    with patch("proxygen_cli.cli.command_main.SETTINGS", Settings()):
        with patch(
            "proxygen_cli.lib.proxygen_api.requests.Session.request"
        ) as _request:
            _request.return_value = mock_response("text", {"mock_return": "value"}, 200)
            result = runner.invoke(status)

    assert json.loads(result.output) == {
        "proxygen_url": "https://mock-proxygen.nhs.uk",
        "response": {"mock_return": "value"},
    }
