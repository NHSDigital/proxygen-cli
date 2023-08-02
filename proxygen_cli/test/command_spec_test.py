"""
Tests around the spec CLI command.
"""
from urllib.parse import urlparse
from click.testing import CliRunner

from proxygen_cli.cli.command_spec import get as spec_get, \
    delete as spec_delete, publish as spec_publish


def test_publish_spec_std(patch_request, patch_access_token,
                          patch_spec_resolver, patch_click_confirm):
    """
    Ensure the publish doesn't use UAT specs by default.
    """

    runner = CliRunner()
    with patch_access_token(), patch_request(200, "TEST") as patched_request,\
            patch_spec_resolver(), patch_click_confirm():

        runner.invoke(spec_publish, ["NoFile"], obj={"api": "mock-api"})

        path = _extract_request_path(patched_request, "PUT")

        assert path == "/apis/mock-api/spec"


def test_publish_spec_uat(patch_request, patch_access_token,
                          patch_spec_resolver, patch_click_confirm):
    """
    Ensure the publish` command supports UAT specs.
    """

    runner = CliRunner()
    with patch_access_token(), patch_request(200, "TEST") as patched_request,\
            patch_spec_resolver(), patch_click_confirm():

        runner.invoke(
            spec_publish,
            ["NoFile", "--uat"],
            obj={"api": "mock-api"}
        )

        path = _extract_request_path(patched_request, "PUT")

        assert path == "/apis/mock-api/spec/uat"


def test_get_spec_std(patch_request, patch_access_token):
    """
    Ensure the get command supports UAT specs.
    """

    runner = CliRunner()
    with patch_access_token(), patch_request(200, "TEST") as patched_request:

        runner.invoke(spec_get, obj={"api": "mock-api"})

        path = _extract_request_path(patched_request)

        assert path == "/apis/mock-api/spec"


def test_get_spec_uat(patch_request, patch_access_token):
    """
    Ensure the get command supports UAT specs.
    """

    runner = CliRunner()
    with patch_access_token(), patch_request(200, "TEST") as patched_request:

        runner.invoke(spec_get, ["--uat"], obj={"api": "mock-api"})

        path = _extract_request_path(patched_request)

        assert path == "/apis/mock-api/spec/uat"


def test_delete_spec_std(patch_request, patch_access_token,
                         patch_click_confirm):
    """
    Ensure the delete method doesn't specify the UAT spec by default.
    """

    runner = CliRunner()
    with patch_access_token(), patch_request(200, "TEST") as patched_request, \
            patch_click_confirm():

        runner.invoke(spec_delete, obj={"api": "mock-api"})

        path = _extract_request_path(patched_request, "DELETE")

        assert path == "/apis/mock-api/spec"


def test_delete_spec_uat(patch_request, patch_access_token,
                         patch_click_confirm):
    """
    Ensure the delete command supports UAT specs.
    """

    runner = CliRunner()
    with patch_access_token(), patch_request(200, "TEST") as patched_request, \
            patch_click_confirm():

        runner.invoke(spec_delete, ["--uat"], obj={"api": "mock-api"})

        path = _extract_request_path(patched_request, "DELETE")

        assert path == "/apis/mock-api/spec/uat"


def _extract_request_path(mocked_request, method='GET'):
    """
    Extract the path from the first mocked call to .get() in the provided
    session.
    """
    for mock_call in mocked_request.mock_calls:
        request_method, request_url = mock_call.args
        if request_method == method:
            return urlparse(request_url).path
