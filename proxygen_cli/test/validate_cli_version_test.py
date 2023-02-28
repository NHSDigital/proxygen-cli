import pytest

from proxygen_cli.lib.version import validate_cli_version


def test_validate_cli_version_success(patch_request):
    required_version = "2.0.5"

    mocked_response = {"proxygen_cli": {"min_version": required_version}}
    with patch_request(200, mocked_response):
        # No assert needed as function will raise if unsuccessful
        validate_cli_version()


def test_validate_cli_version_failure(patch_request):
    required_version = "3.0.0"

    mocked_response = {"proxygen_cli": {"min_version": required_version}}
    with patch_request(200, mocked_response), pytest.raises(RuntimeError) as e:
        validate_cli_version()

        assert (
            str(e.value)
            == "This version proxygen-cli is out-of-date. Please update to 3.0.0"
        )
