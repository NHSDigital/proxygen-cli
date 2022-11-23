"""Proxygen test utility functions"""
import functools
import uuid
from time import time
from urllib.parse import parse_qs, urlparse
import json
import hashlib

import jwt
import requests
from lxml import html

from . import config
from .credentials import ClientCredentials, UserCredentials, MachineUserCredentials, get_client, get_user
from .dot_proxygen import token_cache_file


def cache_key(client, user):
    s = json.dumps({"client": client.dict(), "user": user.dict()})
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _read_cache():
    with token_cache_file().open() as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _write_cache(cache):
    with token_cache_file().open("w") as f:
        return json.dump(cache, f, indent=2)


def access_token():
    now = int(time()) + 10  # give ourselves some leeway

    api = config.get()
    client = get_client(api.client)
    user = get_user(api.user)

    cache = _read_cache()
    _cache_key = cache_key(client, user)
    token_data = cache.get(_cache_key)

    jwt_decode_options = {"verify_signature": False}
    if token_data is not None:
        access_token_payload = jwt.decode(
            token_data["access_token"], options=jwt_decode_options
        )
        if now < access_token_payload["exp"]:
            return token_data["access_token"]
        refresh_token_payload = jwt.decode(
            token_data["refresh_token"], options=jwt_decode_options
        )
        if now < refresh_token_payload["exp"]:
            # can try doing a refresh
            new_token_data = _get_token_data_from_refresh_token(
                client, token_data["refresh_token"]
            )
            if new_token_data is not None:
                cache[_cache_key] = new_token_data
                _write_cache(cache)
                return new_token_data["access_token"]

    # If we get here, no cache hit, or token expired or refresh token call failed.
    # So do full login
    if isinstance(user, UserCredentials):
        token_data = _get_token_data_from_user_login(client, user)
    elif isinstance(user, MachineCredentials):
        token_data = _get_token_data_from_machine
    cache[_cache_key] = token_data
    _write_cache(cache)
    return token_data["access_token"]


def _get_token_data_from_refresh_token(
    client: ClientCredentials, refresh_token: str
):
    token_response = requests.post(
        f"{client.base_url}/protocol/openid-connect/token",
        data={
            "grant_type": "refresh_token",
            "client_id": client.id,
            "client_secret": client.secret,
            "refresh_token": refresh_token,
        },
    )
    if token_response.status_code == 200:
        return token_response.json()


def _get_token_data_from_user_login(
    client: ClientCredentials, user: UserCredentials
):
    session = requests.Session()
    redirect_uri = f"{client.base_url}/protocol/openid-connect/callback"
    login_page_resp = session.get(
        f"{client.base_url}/protocol/openid-connect/auth",
        params={
            "client_id": client.id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": "123",
            "scope": "openid",
        },
    )

    assert (
        login_page_resp.status_code == 200
    ), f"Login page get request status was {login_page_resp.status_code} expected to be 200"

    login_form = html.fromstring(login_page_resp.content.decode()).get_element_by_id(
        "kc-form-login"
    )

    url = login_form.action
    user_login_resp = session.post(
        url,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"username": user.name, "password": user.password, "credentialId": ""},
    )
    assert (
        user_login_resp.status_code == 200,
        f"User password submission returned non-200 response",
    )

    http_error_msg = "Invalid username or password"
    if http_error_msg in user_login_resp.text:
        raise ValueError(http_error_msg)

    querys = urlparse(user_login_resp.history[-1].headers["Location"]).query
    auth_code = parse_qs(querys)["code"]
    if isinstance(auth_code, list):
        auth_code = auth_code[0]

    token_response = session.post(
        f"{client.base_url}/protocol/openid-connect/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": redirect_uri,
            "client_id": client.id,
            "client_secret": client.secret,
        },
    )
    if token_response.status_code != 200:
        raise RuntimeError(
            f"Token response was {token_response.status_code} expected 200"
        )
    return token_response.json()





def _get_token_data_from_machine_user(client, user):
    aud = client.base_url
    token_endpoint = aud + "/protocol/openid-connect/token"
    private_key_file = os.environ["PROXYGEN_MACHINE_USER_CLIENT_PRIVATE_KEY_ABSOLUTE_PATH"]
    with open(private_key_file, "r", encoding="utf-8") as key_file:
        private_key = key_file.read()

    claims = {
        "sub": client_id,
        "iss": client_id,
        "jti": str(uuid.uuid4()),
        "aud": aud,
        "exp": int(time()) + 300,  # 5mins in the future
    }

    client_assertion = jwt.encode(claims, private_key, algorithm="RS512")
    token_response = requests.post(
        token_endpoint,
        data={
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": client_assertion,
        },
    )
    assert token_response.status_code == 200, f"Token response was {token_response.status_code} expected 200"
    return token_response.json()["access_token"]

