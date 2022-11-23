from urllib.parse import urlparse, urljoin
import json

import requests

from . import config, auth
from .constants import LITERAL_ENVS


class ProxygenSession(requests.Session):
    def __init__(self, api_name, **kwargs):
        self.api_config = config.get()
        super().__init__(**kwargs)

    def request(self, method, path, **kwargs):

        if self.api_config.name is not None:
            headers = kwargs.get("headers", {})
            headers["Authorization"] = f"Bearer {auth.access_token()}"
            kwargs["headers"] = headers

        base_url = self.api_config.endpoint_url
        url = urljoin(base_url, path)
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



# SECRET methods
def get_secret(api: str, environment: LITERAL_ENVS, secret_name: str):
    resp = _session(api).get(
        f"/apis/{api}/environments/{environment}/secrets/{secret_name}"
    )
    return resp.json()

def delete_secret(api: str, environment: LITERAL_ENVS, secret_name: str):
    resp = _session(api).delete(
        f"/apis/{api}/environments/{environment}/secrets/{secret_name}"
    )
    return resp.json()
