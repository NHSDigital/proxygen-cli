from typing import Any, Dict, Optional, Literal
from urllib.parse import urlparse, urljoin
import json

import requests
import click
import platform

from proxygen_cli.lib.settings import SETTINGS
from proxygen_cli.lib.auth import access_token
from proxygen_cli import __version__ as proxygen_cli_version
from proxygen_cli import _package_name as proxygen_package_name
from proxygen_cli.lib.constants import LITERAL_ENVS


class ProxygenSession(requests.Session):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def request(self, method, path, **kwargs):

        if path.startswith("/apis/"):
            headers = kwargs.get("headers", {})
            headers["Authorization"] = f"Bearer {access_token()}"
            headers[
                "User-Agent"
            ] = f"{proxygen_package_name}/{proxygen_cli_version} Python/{platform.python_version()}"
            kwargs["headers"] = headers

        url = urljoin(SETTINGS.endpoint_url, path)
        resp = super().request(method, url, **kwargs)
        return resp


_PROXYGEN_SESSION = None


def _session():
    global _PROXYGEN_SESSION
    if _PROXYGEN_SESSION is None:
        _PROXYGEN_SESSION = ProxygenSession()
    return _PROXYGEN_SESSION


def _resp_json(resp, none_on_404=True):
    if resp.status_code == 200:
        if resp.text:
            return resp.json()
        return ""
    elif none_on_404 and resp.status_code == 404:
        return None
    else:
        body = resp.text
        try:
            body = json.loads(resp.text)
        except json.JSONDecodeError:
            pass
        error_dict = {
            "error": "Unexpected response from proxygen server",
            "request": {
                "url": str(resp.request.url),
                "method": resp.request.method,
            },
            "response": {
                "status_code": resp.status_code,
                "body": body,
            },
        }

        raise click.ClickException(json.dumps(error_dict))


def status():
    resp = _session().get("/_status")
    return _resp_json(resp)


def get_api(api):
    resp = _session().get(f"/apis/{api}")
    return _resp_json(resp)


def get_docker_login(api: str):
    resp = _session().get(f"/apis/{api}/docker-token")
    return _resp_json(resp)


def get_resources(
    api: str,
    _type: Optional[Literal["instance", "secret"]] = None,
):
    """
    Get both resource types across all envs.
    Optionally filter with `_type`.
    """
    params = {}
    if _type:
        params["type"] = _type
    resp = _session().get(f"/apis/{api}/environments", params=params)
    return _resp_json(resp)


def get_instances(api: str, environment: LITERAL_ENVS):
    resp = _session().get(f"/apis/{api}/environments/{environment}/instances")
    return _resp_json(resp)


def get_secrets(api: str, environment: LITERAL_ENVS):
    resp = _session().get(f"/apis/{api}/environments/{environment}/secrets")
    return _resp_json(resp)


# INSTANCE methods
def get_instance(api: str, environment: LITERAL_ENVS, instance_name: str):
    resp = _session().get(
        f"/apis/{api}/environments/{environment}/instances/{instance_name}"
    )
    return _resp_json(resp)


def delete_instance(api: str, environment: LITERAL_ENVS, instance_name: str):
    resp = _session().delete(
        f"/apis/{api}/environments/{environment}/instances/{instance_name}"
    )
    return _resp_json(resp)


def put_instance(
    api: str, environment: LITERAL_ENVS, instance: str, paas_open_api: Dict[str, Any]
):

    resp = _session().put(
        f"/apis/{api}/environments/{environment}/instances/{instance}",
        data=json.dumps(paas_open_api, default=str),
        headers={"Content-Type": "application/json"},
    )
    return _resp_json(resp)


# SPEC methods
def get_spec(api: str):
    resp = _session().get(f"/apis/{api}/spec")
    return _resp_json(resp)


def delete_spec(api: str):
    resp = _session().delete(f"/apis/{api}/spec")
    return _resp_json(resp)


def put_spec(api: str, paas_open_api: Dict[str, Any]):
    resp = _session().put(
        f"/apis/{api}/spec",
        data=json.dumps(paas_open_api, default=str),
        headers={"Content-Type": "application/json"},
    )
    return _resp_json(resp)


# SECRET methods
def get_secret(api: str, environment: LITERAL_ENVS, secret_name: str):
    resp = _session().get(
        f"/apis/{api}/environments/{environment}/secrets/{secret_name}"
    )
    return _resp_json(resp)


def put_secret(
    api: str,
    environment: LITERAL_ENVS,
    secret_name: str,
    secret_value: str,
    _type: str = None,
):

    params = {}
    if _type:
        params["type"] = _type
    resp = _session().put(
        f"/apis/{api}/environments/{environment}/secrets/{secret_name}",
        data=secret_value,
        params=params,
    )
    return _resp_json(resp)


def delete_secret(api: str, environment: LITERAL_ENVS, secret_name: str):
    resp = _session().delete(
        f"/apis/{api}/environments/{environment}/secrets/{secret_name}"
    )
    return _resp_json(resp)
