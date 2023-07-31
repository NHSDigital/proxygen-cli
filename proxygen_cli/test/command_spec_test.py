from unittest.mock import patch
from click.testing import CliRunner

from proxygen_cli.cli.command_spec import get as spec_get
from proxygen_cli.test.command_credentials_test import get_test_credentials


def test_get_spec_std(patch_proxygen_session, patch_access_token):
    """
    Ensure the get command supports UAT specs.
    """

    runner = CliRunner()
    with patch_access_token(), patch_proxygen_session() as patched_session:

        runner.invoke(spec_get, obj={"api": "mock-api"})

        path = _extract_get_path(patched_session)

        assert path == "/apis/mock-api/spec"


def test_get_spec_uat(patch_proxygen_session, patch_access_token):
    """
    Ensure the get command supports UAT specs.
    """

    runner = CliRunner()
    with patch_access_token(), patch_proxygen_session() as patched_session:

        runner.invoke(spec_get, ["--uat"], obj={"api": "mock-api"})

        path = _extract_get_path(patched_session)

        assert path == "/apis/mock-api/spec/uat"


def _extract_get_path(mocked_session):
    """
    Extract the path from the first mocked call to .get() in the provided
    session.
    """
    for mock_call in mocked_session.mock_calls:
        if mock_call[0] == "().get":
            return mock_call[1][0]
