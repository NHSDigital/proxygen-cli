import os
from urllib.parse import urlparse

from click.testing import CliRunner

import proxygen_cli.cli.command_secret as cmd_secret

API_NAME = "mock-api"
API_ENV = "internal-dev"
SECRET_NAME = "test-secret"


def _parse_fixture(filename):

    test_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = f"{test_dir}/fixtures/{filename}"

    with open(file_path, "r", encoding="utf-8") as f_desc:
        return file_path, f_desc.read()


def _url_path(url) -> str:
    """
    Strip the path from a URL.
    :param url: The URL to strip.
    :return: The URL without the path.
    """
    parsed = urlparse(url)
    return parsed.path


def test_secret_put_file(patch_access_token, patch_request):
    """
    Ensure that the PUT request for secrets contains the expected fields
    and is to the correct URL.
    """
    runner = CliRunner()

    file_path, file_contents = _parse_fixture("secret.txt")

    with patch_access_token(), patch_request(200, {}) as patched_request:
        runner.invoke(
            cmd_secret.put,
            [
                API_ENV,
                "test-secret",
                "--secret-file",
                file_path
            ],
            obj={"api": API_NAME},
        )

        _, (verb, url), content = patched_request.mock_calls[0]
        assert verb == "PUT"
        assert _url_path(url) \
            == f"/apis/{API_NAME}/environments/{API_ENV}/secrets/{SECRET_NAME}"
        assert file_contents == content['data']
        assert content['params'] == {}


def test_secret_put_apikey(patch_access_token, patch_request):
    """
    Ensure that the PUT request for an apikey secret contains the expected
    fields and is to the correct URL. Doucbles as a test for the --secret-value
    option.
    """
    runner = CliRunner()
    secret_value = "TESTSECRET"

    with patch_access_token(), patch_request(200, {}) as patched_request:
        runner.invoke(
            cmd_secret.put,
            [
                API_ENV,
                "test-secret",
                "--apikey",
                "--secret-value",
                secret_value
            ],
            obj={"api": API_NAME},
        )

        _, (verb, url), content = patched_request.mock_calls[0]
        assert verb == "PUT"
        assert _url_path(url) \
            == f"/apis/{API_NAME}/environments/{API_ENV}/secrets/{SECRET_NAME}"
        assert content['params']['type'] == 'apikey'
        assert content['data'] == secret_value


def test_secret_put_mtls(patch_access_token, patch_request):
    """
    Ensure that the PUT request for an mtls secret validates the parameters
    correctly, contains the expected fields and is to the correct URL.

    """
    runner = CliRunner()

    key_path, key_contents = _parse_fixture("client.key")
    cert_path, cert_contents = _parse_fixture("client.pem")

    with patch_access_token(), patch_request(200, {}) as patched_request:
        runner.invoke(
            cmd_secret.put,
            [
                API_ENV,
                "test-secret",
                "--mtls-cert", cert_path,
                "--mtls-key", key_path
            ],
            obj={"api": API_NAME},
        )

        _, (verb, url), content = patched_request.mock_calls[0]
        assert verb == "PUT"
        assert _url_path(url) \
            == f"/apis/{API_NAME}/environments/{API_ENV}/secrets/{SECRET_NAME}"
        assert content['params']['type'] == 'mtls'
        assert content['files']['cert'] == ('cert.pem', cert_contents)
        assert content['files']['key'] == ('key.pem', key_contents)
