from typing import Any, Dict
from urllib.parse import urlparse, urljoin
import json

import requests

from proxygen_cli.lib.settings import SETTINGS
from proxygen_cli.lib.auth import access_token
from proxygen_cli.lib.constants import LITERAL_ENVS


class ProxygenSession(requests.Session):
    def __init__(self, api_name, **kwargs):
        super().__init__(**kwargs)

    def request(self, method, path, **kwargs):

        if path.startswith("/apis/"):
            headers = kwargs.get("headers", {})
            headers["Authorization"] = f"Bearer {access_token()}"
            kwargs["headers"] = headers

        url = urljoin(SETTINGS.endpoint_url, path)
        resp = super().request(method, url, **kwargs)
        return resp


_PROXYGEN_SESSIONS = {}


def _session(api):
    global _PROXYGEN_SESSIONS
    if api not in _PROXYGEN_SESSIONS:
        _PROXYGEN_SESSIONS[api] = ProxygenSession(api)
    return _PROXYGEN_SESSIONS[api]


def status():
    resp = _session(None).get("/_status")
    return resp.json()


def get_api(api):
    resp = _session(api).get(f"/apis/{api}")
    return resp.json()


def get_api_environment(api: str, environment: LITERAL_ENVS):
    resp = _session(api).get(f"/apis/{api}/environments/{environment}")
    return resp.json()


def get_instances(api: str, environment: LITERAL_ENVS, instance_name: str):
    resp = _session(api).get(f"/apis/{api}/environments/{environment}/instances")
    return resp.json()



# INSTANCE methods
def get_instance(api: str, environment: LITERAL_ENVS, instance_name: str):
    resp = _session(api).get(
        f"/apis/{api}/environments/{environment}/instances/{instance_name}"
    )
    return resp.json()

def delete_instance(api: str, environment: LITERAL_ENVS, instance_name: str):
    resp = _session(api).delete(
        f"/apis/{api}/environments/{environment}/instances/{instance_name}"
    )
    try:
        return resp.json()
    except json.JSONDecodeError:
        pass

def put_instance(api: str, environment: LITERAL_ENVS, instance: str, paas_open_api: Dict[str, Any]):
    resp = _session(api).put(
        f"/apis/{api}/environments/{environment}/instances/{instance}",
        json=paas_open_api,
    )
    return resp.json()



# SECRET methods
def get_secret(api: str, environment: LITERAL_ENVS, secret_name: str):
    resp = _session(api).get(
        f"/apis/{api}/environments/{environment}/secrets/{secret_name}"
    )
    return resp.json()

def put_secret(api: str, environment: LITERAL_ENVS, secret_name: str, secret_value: str, _type: str = None):

    params = {}
    if _type:
        params["type"] = _type
    resp = _session(api).put(
        f"/apis/{api}/environments/{environment}/secrets/{secret_name}",
        data=secret_value,
        params=params,
    )
    return resp.json()

def delete_secret(api: str, environment: LITERAL_ENVS, secret_name: str):
    resp = _session(api).delete(
        f"/apis/{api}/environments/{environment}/secrets/{secret_name}"
    )
    return resp.json()
