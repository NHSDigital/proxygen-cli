from unittest.mock import patch

import pytest

from proxygen_cli.lib.version import validate_cli_version


def test_validate_cli_version_success(mock_response):
    required_version = "2.0.5"

    mocked_response = {"proxygen_cli": {"min_version": required_version}}
    with patch("proxygen_cli.lib.proxygen_api.requests.Session.request") as _request:
        _request.return_value = mock_response("text", mocked_response, 200)

        # No assert needed as function will raise if unsuccessful
        validate_cli_version()


def test_validate_cli_version_failure(mock_response):
    required_version = "3.0.0"

    mocked_response = {"proxygen_cli": {"min_version": required_version}}
    with patch("proxygen_cli.lib.proxygen_api.requests.Session.request") as _request:
        _request.return_value = mock_response("text", mocked_response, 200)

        with pytest.raises(RuntimeError) as e:
            validate_cli_version()

        assert (
            str(e.value)
            == "This version proxygen-cli is out-of-date. Please update to 3.0.0"
        )
