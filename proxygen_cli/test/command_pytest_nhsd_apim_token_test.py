"""
Tests around the pytest_nhsd_apim_token CLI command.
"""

import json

from click.testing import CliRunner

import proxygen_cli.cli.command_pytest_nhsd_apim_token as cmd_pytest_nhsd_apim


def test_get_pytest_nhsd_apim_token(patch_request, patch_access_token):
    """
    Ensure the get command supports UAT specs.
    """
    expected_resp = {"pytest_nhsd_apim_token": "token123", "expires_in": "3600"}

    runner = CliRunner()
    with patch_access_token(), patch_request(200, expected_resp):
        result = runner.invoke(cmd_pytest_nhsd_apim.get_token, obj={"api": "mock-api"})

    result_to_dict = json.loads(result.output.strip())
    assert result_to_dict == expected_resp
