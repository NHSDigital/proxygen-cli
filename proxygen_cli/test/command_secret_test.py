import os
from urllib.parse import urlparse

from click.testing import CliRunner

import proxygen_cli.cli.command_secret as cmd_secret
import pytest
import click

API_NAME = "mock-api"
API_ENV = "internal-dev"
SECRET_NAME = "test-secret"
MTLS_TYPE = "mtls"
APIKEY_TYPE = "apikey"


class TestSecretCliCommands:
    """
    Tets related to specific workflows around secrets management with the CLI.
    """

    @staticmethod
    def _parse_fixture(filename):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = f"{test_dir}/fixtures/{filename}"

        with open(file_path, "r", encoding="utf-8") as f_desc:
            return file_path, f_desc.read()

    @staticmethod
    def _url_path(url) -> str:
        """
        Strip the path from a URL.
        :param url: The URL to strip.
        :return: The URL without the path.
        """
        parsed = urlparse(url)
        return parsed.path

    def test_secret_put_file(self, patch_access_token, patch_request):
        """
        Ensure that the PUT request for secrets contains the expected fields
        and is to the correct URL.
        """
        runner = CliRunner()

        file_path, file_contents = self._parse_fixture("secret.txt")

        with patch_access_token(), patch_request(200, {}) as patched_request:
            runner.invoke(
                cmd_secret.put,
                [API_ENV, "test-secret", "--apikey", "--secret-file", file_path],
                obj={"api": API_NAME},
                catch_exceptions=False,
            )

            _, (verb, url), content = patched_request.mock_calls[0]
            assert verb == "PUT"
            assert self._url_path(url) == (
                f"/apis/{API_NAME}/environments"
                f"/{API_ENV}/secrets/{APIKEY_TYPE}/{SECRET_NAME}"
            )
            assert file_contents == content["data"]

    def test_secret_put_apikey(self, patch_access_token, patch_request):
        """
        Ensure that the PUT request for an apikey secret contains the expected
        fields and is to the correct URL. Doucbles as a test for the
        --secret-value option.
        """
        runner = CliRunner()
        secret_value = "TESTSECRET"

        with patch_access_token(), patch_request(200, {}) as patched_request:
            runner.invoke(
                cmd_secret.put,
                [API_ENV, "test-secret", "--apikey", "--secret-value", secret_value],
                obj={"api": API_NAME},
                catch_exceptions=False,
            )

            assert patched_request.call_count == 1, "Mock request not made"
            _, (verb, url), content = patched_request.mock_calls[0]
            assert verb == "PUT"
            assert self._url_path(url) == (
                f"/apis/{API_NAME}/environments"
                f"/{API_ENV}/secrets/{APIKEY_TYPE}/{SECRET_NAME}"
            )
            assert content["data"] == secret_value

    def test_secret_put_mtls(self, patch_access_token, patch_request):
        """
        Ensure that the PUT request for an mtls secret validates the parameters
        correctly, contains the expected fields and is to the correct URL.

        """
        runner = CliRunner()

        key_path, key_contents = self._parse_fixture("client.key")
        cert_path, cert_contents = self._parse_fixture("client.pem")

        with patch_access_token(), patch_request(200, {}) as patched_request:
            runner.invoke(
                cmd_secret.put,
                [
                    API_ENV,
                    "test-secret",
                    "--mtls-cert",
                    cert_path,
                    "--mtls-key",
                    key_path,
                ],
                obj={"api": API_NAME},
                catch_exceptions=False,
            )

            _, (verb, url), content = patched_request.mock_calls[0]
            assert verb == "PUT"
            assert self._url_path(url) == (
                f"/apis/{API_NAME}/environments"
                f"/{API_ENV}/secrets/{MTLS_TYPE}/{SECRET_NAME}"
            )
            assert content["files"]["cert"] == ("cert.pem", cert_contents)
            assert content["files"]["key"] == ("key.pem", key_contents)


class TestPutOptionValidation:
    """
    Tests for the command_secret._validate_put_options() function.
    """

    # Defining these outside of the code we're testing makes us resilient to
    # inadvertent error message changes.
    ERR_TYPE_CONFLICT = (
        "Please specify either of --secret-value and --secret-file, "
        "or --mtls-cert with --mtls-key."
    )
    ERR_MTLS_BOTH = "Please specify both --mtls-cert and --mtls-key."
    ERR_FILE_OR_VALUE = (
        "Please specify one of --secret-value" " and --secret-file, not both."
    )

    # pylint: disable=protected-access

    def test_no_options(self):
        """
        Ensure that the function raises an exception if no options are
        provided.
        """
        with pytest.raises(click.UsageError) as ex:
            cmd_secret._validate_put_options(None, None, None, None, None)
        assert ex.value.message == self.ERR_TYPE_CONFLICT

    def test_cert_no_key(self):
        """
        Ensure that we can't provide only a mTLS cert
        """
        with pytest.raises(click.UsageError) as ex:
            cmd_secret._validate_put_options(None, None, None, "TEST", None)
        assert ex.value.message == self.ERR_MTLS_BOTH

    def test_key_no_cert(self):
        """
        Ensure that we can't provide only a mTLS key
        """
        with pytest.raises(click.UsageError) as ex:
            cmd_secret._validate_put_options(None, None, None, None, "TEST")
        assert ex.value.message == self.ERR_MTLS_BOTH

    def test_value_and_mtls(self):
        """
        Ensure that we can't provide value and mTLS details
        """
        with pytest.raises(click.UsageError) as ex:
            cmd_secret._validate_put_options("TEST", None, None, "TEST", "TEST")
        assert ex.value.message == self.ERR_TYPE_CONFLICT

    def test_file_and_mtls(self):
        """
        Ensure that we can't provide file and mTLS details
        """
        with pytest.raises(click.UsageError) as ex:
            cmd_secret._validate_put_options(None, "TEST", None, "TEST", "TEST")
        assert ex.value.message == self.ERR_TYPE_CONFLICT

    def test_file_and_value_and_mtls(self):
        """
        Ensure that we can't provide file, value and mTLS details
        """
        with pytest.raises(click.UsageError) as ex:
            cmd_secret._validate_put_options("TEST", "TEST", None, "TEST", "TEST")
        assert ex.value.message == self.ERR_TYPE_CONFLICT

    def test_value_and_file(self):
        """
        Ensure that we can't provide value and file
        """
        with pytest.raises(click.UsageError) as ex:
            cmd_secret._validate_put_options("TEST", "TEST", None, None, None)
        assert ex.value.message == self.ERR_FILE_OR_VALUE
