from unittest.mock import patch

from click.testing import CliRunner

import proxygen_cli.cli.command_instance as cmd_instance

MOCK_INSTANCE_LIST = [
    {
        "environment": "int",
        "type": "instance",
        "name": "gp-registrations-mi",
        "last_modified": "2023-02-27T15:46:11+00:00",
        "spec_hash": "59428141168ca28d0c383d243ccd1a4c",
    },
    {
        "environment": "internal-dev-sandbox",
        "type": "instance",
        "name": "gp-registrations-mi-109",
        "last_modified": "2023-02-10T09:47:18+00:00",
        "spec_hash": "f577618d5ad0aa1b270c7de8c818ae86",
    },
    {
        "environment": "internal-dev-sandbox",
        "type": "instance",
        "name": "gp-registrations-mi-110",
        "last_modified": "2023-02-10T13:28:08+00:00",
        "spec_hash": "9973d1381467bfa27bfc34627eea515a",
    },
    {
        "environment": "internal-dev-sandbox",
        "type": "instance",
        "name": "gp-registrations-mi-111",
        "last_modified": "2023-02-10T13:53:31+00:00",
        "spec_hash": "485cfea811e0b12400d195ab607a9789",
    },
    {
        "environment": "internal-dev-sandbox",
        "type": "instance",
        "name": "gp-registrations-mi-112",
        "last_modified": "2023-02-22T09:10:30+00:00",
        "spec_hash": "1d21792c2cf1d40a0ea94103eafeb35c",
    },
    {
        "environment": "internal-dev-sandbox",
        "type": "instance",
        "name": "gp-registrations-mi",
        "last_modified": "2023-02-27T15:44:46+00:00",
        "spec_hash": "8ef77a8c32e032ecb61da67de710847b",
    },
    {
        "environment": "internal-dev",
        "type": "instance",
        "name": "gp-registrations-mi-109",
        "last_modified": "2023-02-10T09:47:09+00:00",
        "spec_hash": "7c38041567976fa5a961c2bc69d7a08a",
    },
    {
        "environment": "internal-dev",
        "type": "instance",
        "name": "gp-registrations-mi-110",
        "last_modified": "2023-02-10T13:28:02+00:00",
        "spec_hash": "34c14569aae7d02cf790495724064cd9",
    },
    {
        "environment": "internal-dev",
        "type": "instance",
        "name": "gp-registrations-mi-111",
        "last_modified": "2023-02-10T13:48:09+00:00",
        "spec_hash": "df738b4c3009d8de02c466bf0dc6e8e6",
    },
    {
        "environment": "internal-dev",
        "type": "instance",
        "name": "gp-registrations-mi-112",
        "last_modified": "2023-02-22T09:10:29+00:00",
        "spec_hash": "febfb157ef305827b528eb51c614da83",
    },
    {
        "environment": "internal-dev",
        "type": "instance",
        "name": "gp-registrations-mi",
        "last_modified": "2023-02-27T15:44:49+00:00",
        "spec_hash": "573fa4b4a7af8058707a3acd617d08f7",
    },
    {
        "environment": "prod",
        "type": "instance",
        "name": "gp-registrations-mi",
        "last_modified": "2023-02-10T15:46:20+00:00",
        "spec_hash": "1b7991084da896e23acf4bf0af4068a3",
    },
    {
        "environment": "sandbox",
        "type": "instance",
        "name": "gp-registrations-mi",
        "last_modified": "2023-02-27T15:46:10+00:00",
        "spec_hash": "31e4f4f2c85f133dd0ffb194c14c8bae",
    },
]


@patch("proxygen_cli.lib.proxygen_api.status")
def test_instance_list(_, patch_access_token, patch_request):
    runner = CliRunner()
    with patch_access_token():
        with patch_request(200, MOCK_INSTANCE_LIST):
            result = runner.invoke(cmd_instance.list, obj={"api": "mock-api"})

    assert result.output.strip() == "\n".join(
        [
            "environment           type      name                     spec_hash                         last_modified",
            "--------------------  --------  -----------------------  --------------------------------  ----------------",
            "internal-dev          instance  gp-registrations-mi-109  7c38041567976fa5a961c2bc69d7a08a  2023-02-10 09:47",
            "internal-dev-sandbox  instance  gp-registrations-mi-109  f577618d5ad0aa1b270c7de8c818ae86  2023-02-10 09:47",
            "internal-dev          instance  gp-registrations-mi-110  34c14569aae7d02cf790495724064cd9  2023-02-10 13:28",
            "internal-dev-sandbox  instance  gp-registrations-mi-110  9973d1381467bfa27bfc34627eea515a  2023-02-10 13:28",
            "internal-dev          instance  gp-registrations-mi-111  df738b4c3009d8de02c466bf0dc6e8e6  2023-02-10 13:48",
            "internal-dev-sandbox  instance  gp-registrations-mi-111  485cfea811e0b12400d195ab607a9789  2023-02-10 13:53",
            "prod                  instance  gp-registrations-mi      1b7991084da896e23acf4bf0af4068a3  2023-02-10 15:46",
            "internal-dev          instance  gp-registrations-mi-112  febfb157ef305827b528eb51c614da83  2023-02-22 09:10",
            "internal-dev-sandbox  instance  gp-registrations-mi-112  1d21792c2cf1d40a0ea94103eafeb35c  2023-02-22 09:10",
            "internal-dev-sandbox  instance  gp-registrations-mi      8ef77a8c32e032ecb61da67de710847b  2023-02-27 15:44",
            "internal-dev          instance  gp-registrations-mi      573fa4b4a7af8058707a3acd617d08f7  2023-02-27 15:44",
            "sandbox               instance  gp-registrations-mi      31e4f4f2c85f133dd0ffb194c14c8bae  2023-02-27 15:46",
            "int                   instance  gp-registrations-mi      59428141168ca28d0c383d243ccd1a4c  2023-02-27 15:46",
        ]
    )


def test_instance_list_with_env(patch_request, patch_access_token):
    env = "internal-dev"

    runner = CliRunner()
    with patch_access_token():
        filtered_envs = [
            e for e in MOCK_INSTANCE_LIST if e.get("environment") == "internal-dev"
        ]
        with patch_request(200, filtered_envs):
            result = runner.invoke(
                cmd_instance.list, ["--env", env], obj={"api": "mock-api"}
            )

    assert result.output.strip() == "\n".join(
        [
            "environment    type      name                     spec_hash                         last_modified",
            "-------------  --------  -----------------------  --------------------------------  ----------------",
            "internal-dev   instance  gp-registrations-mi-109  7c38041567976fa5a961c2bc69d7a08a  2023-02-10 09:47",
            "internal-dev   instance  gp-registrations-mi-110  34c14569aae7d02cf790495724064cd9  2023-02-10 13:28",
            "internal-dev   instance  gp-registrations-mi-111  df738b4c3009d8de02c466bf0dc6e8e6  2023-02-10 13:48",
            "internal-dev   instance  gp-registrations-mi-112  febfb157ef305827b528eb51c614da83  2023-02-22 09:10",
            "internal-dev   instance  gp-registrations-mi      573fa4b4a7af8058707a3acd617d08f7  2023-02-27 15:44",
        ]
    )


def test_instance_deploy_no_confirm(patch_pathlib, patch_request):
    env = "internal-dev"

    runner = CliRunner()
    with patch(
        "proxygen_cli.lib.proxygen_api.access_token"
    ) as _access_token, patch_request(200, {}), patch_pathlib(
        "test-yaml-key: test-yaml-value"
    ):
        _access_token.return_value = "12345"
        result = runner.invoke(
            cmd_instance.deploy,
            [env, "mock-api-base-path", "specification/mock-api-spec", "--no-confirm"],
            obj={"api": "mock-api"},
        )

    assert (
        "✔ Deploying https://internal-dev.api.service.nhs.uk/mock-api-base-path"
        in result.output.strip()
    )


def test_instance_deploy_with_confirm(patch_pathlib, patch_access_token, patch_request):
    env = "internal-dev"

    runner = CliRunner()
    with patch_access_token(), patch_request(200, {}), patch_pathlib(
        "test-yaml-key: test-yaml-value"
    ):
        result = runner.invoke(
            cmd_instance.deploy,
            [env, "mock-api-base-path", "specification/mock-api-spec"],
            obj={"api": "mock-api"},
        )

    assert "Aborted!" in result.output.strip()


def test_instance_deploy_invalid_instance_name(patch_pathlib, patch_access_token, patch_request):
    env = "internal-dev"

    runner = CliRunner()
    with patch(
        "proxygen_cli.lib.proxygen_api.access_token"
    ) as _access_token, patch_request(404, {}), patch_pathlib(
        "test-yaml-key: test-yaml-value"
    ):
        _access_token.return_value = "12345"
        result = runner.invoke(
            cmd_instance.deploy,
            [env, "mock-api-base-path", "specification/mock-api-spec", "--no-confirm"],
            obj={"api": "mock-api"},
        )

    assert (
        "Invalid instance https://internal-dev.api.service.nhs.uk/mock-api-base-path"
        in result.output.strip())


def test_instance_deploy_invalid_base_path(patch_pathlib, patch_access_token, patch_request):
    env = "internal-dev"

    runner = CliRunner()
    with patch(
        "proxygen_cli.lib.proxygen_api.access_token"
    ) as _access_token, patch_request(404, {}), patch_pathlib(
        "test-yaml-key: test-yaml-value"
    ):
        _access_token.return_value = "12345"
        result = runner.invoke(
            cmd_instance.deploy,
            [env, "mock-api/base/path", "specification/mock-api-spec", "--no-confirm"],
            obj={"api": "mock-api"},
        )
    assert (
        "Multipart base paths must include '_' instead of '/'. " +
        "This is to ensure a path-safe version. Proxygen will convert these underscores back in to '/' for the proxy."
        in result.output.strip())


def test_instance_deploy_valid_multipart_base_path(patch_pathlib, patch_access_token, patch_request):
    env = "internal-dev"

    runner = CliRunner()
    with patch(
        "proxygen_cli.lib.proxygen_api.access_token"
    ) as _access_token, patch_request(200, {}), patch_pathlib(
        "test-yaml-key: test-yaml-value"
    ):
        _access_token.return_value = "12345"
        result = runner.invoke(
            cmd_instance.deploy,
            [env, "mock-api_base_path", "specification/mock-api-spec", "--no-confirm"],
            obj={"api": "mock-api"},
        )
    assert (
        "✔ Deploying https://internal-dev.api.service.nhs.uk/mock-api_base_path"
        in result.output.strip()
    )


def test_instance_get(patch_request, patch_pathlib, patch_access_token):
    env = "internal-dev"

    runner = CliRunner()
    with patch_access_token(), patch_request(
        200, "mocked-spec-yaml: mocked-spec-goes-here"
    ), patch_pathlib("test-yaml-key: test-yaml-value"):
        result = runner.invoke(
            cmd_instance.get,
            ["internal-dev", "gp-registrations-mi-109"],
            obj={"api": "mock-api"},
        )

    assert "mocked-spec-yaml: mocked-spec-goes-here" in result.output.strip()


def test_instance_delete_no_confirm(patch_request, patch_pathlib, patch_access_token):
    env = "internal-dev"
    base_path = "mock-api-base-path"
    instance_name = "gp-registrations-mi"

    # Mock the instance to be deleted
    mock_instance = {
        "environment": env,
        "type": "instance",
        "name": instance_name,
        "last_modified": "2023-02-27T15:46:10+00:00",
        "spec_hash": "31e4f4f2c85f133dd0ffb194c14c8bae",
    }

    runner = CliRunner()
    with patch_access_token(), patch_request(200, mock_instance), patch_pathlib(
        "test-yaml-key: test-yaml-value"
    ):
        result = runner.invoke(
            cmd_instance.delete,
            [env, base_path, "--no-confirm"],
            obj={"api": "mock-api"},
        )

    assert "✔ Deleting https://internal-dev.api.service.nhs.uk/mock-api-base-path" in result.output.strip()


def test_instance_delete_with_confirm(patch_request, patch_pathlib, patch_access_token):
    env = "internal-dev"
    base_path = "mock-api-base-path"
    instance_name = "gp-registrations-mi"

    # Mock the instance to be deleted
    mock_instance = {
        "environment": env,
        "type": "instance",
        "name": instance_name,
        "last_modified": "2023-02-27T15:46:10+00:00",
        "spec_hash": "31e4f4f2c85f133dd0ffb194c14c8bae",
    }

    runner = CliRunner()
    with patch_access_token(), patch_request(200, mock_instance), patch_pathlib(
        "test-yaml-key: test-yaml-value"
    ), patch("click.confirm", return_value=True):
        result = runner.invoke(
            cmd_instance.delete,
            [env, base_path],
            obj={"api": "mock-api"},
        )

    assert "✔ Deleting https://internal-dev.api.service.nhs.uk/mock-api-base-path" in result.output.strip()


def test_instance_delete_invalid_instance_name(patch_request, patch_pathlib, patch_access_token):
    env = "internal-dev"

    runner = CliRunner()
    with patch_access_token(), patch_request(404, {}), patch_pathlib(
        "test-yaml-key: test-yaml-value"
    ):
        result = runner.invoke(
            cmd_instance.delete,
            [env, "mock-api-base-path", "--no-confirm"],
            obj={"api": "mock-api"},
        )

    assert "No such instance https://internal-dev.api.service.nhs.uk/mock-api-base-path" in result.output.strip()
