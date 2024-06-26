"""Proxygen test utility functions"""
import hashlib
import json
import uuid
from time import time
from urllib.parse import parse_qs, urlparse

import jwt
import requests
from lxml import html

from .credentials import get_credentials
from .dot_proxygen import token_cache_file


def cache_key():
    s = get_credentials().json()
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

    cache = _read_cache()
    _cache_key = cache_key()
    token_data = cache.get(_cache_key)

    jwt_decode_options = {"verify_signature": False}
    if token_data is not None:
        access_token_payload = jwt.decode(
            token_data["access_token"], options=jwt_decode_options
        )
        if now < access_token_payload["exp"]:
            return token_data["access_token"]
        if "refresh_token" in token_data:
            refresh_token_payload = jwt.decode(
                token_data["refresh_token"], options=jwt_decode_options
            )
            if now < refresh_token_payload["exp"]:
                # can try doing a refresh
                new_token_data = _get_token_data_from_refresh_token(
                    token_data["refresh_token"]
                )
                if new_token_data is not None:
                    cache[_cache_key] = new_token_data
                    _write_cache(cache)
                    return new_token_data["access_token"]

    # If we get here, no cache hit, or token expired or refresh token call failed.
    # So do full login
    CREDENTIALS = get_credentials()
    if CREDENTIALS.username and CREDENTIALS.password:
        token_data = _get_token_data_from_user_login()
    else:
        token_data = _get_token_data_from_machine_user()
    cache[_cache_key] = token_data
    _write_cache(cache)
    return token_data["access_token"]


def _get_token_data_from_refresh_token(refresh_token: str):
    CREDENTIALS = get_credentials()
    token_response = requests.post(
        f"{CREDENTIALS.base_url}/protocol/openid-connect/token",
        data={
            "grant_type": "refresh_token",
            "client_id": CREDENTIALS.client_id,
            "client_secret": CREDENTIALS.client_secret,
            "refresh_token": refresh_token,
        },
    )
    if token_response.status_code == 200:
        return token_response.json()


def _get_token_data_from_user_login():
    session = requests.Session()
    CREDENTIALS = get_credentials()
    redirect_uri = f"{CREDENTIALS.base_url}/callback"
    login_page_resp = session.get(
        f"{CREDENTIALS.base_url}/protocol/openid-connect/auth",
        params={
            "client_id": CREDENTIALS.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": "123",
            "scope": "openid",
        },
    )

    if login_page_resp.status_code != 200:
        raise RuntimeError(
            f"Login page get request status was {login_page_resp.status_code} expected to be 200"
        )

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
        data={
            "username": CREDENTIALS.username,
            "password": CREDENTIALS.password,
            "credentialId": "",
        },
    )

    http_error_msg = "Invalid username or password"
    if http_error_msg in user_login_resp.text:
        raise ValueError(http_error_msg)

    querys = urlparse(user_login_resp.history[-1].headers["Location"]).query
    auth_code = parse_qs(querys)["code"]
    if isinstance(auth_code, list):
        auth_code = auth_code[0]

    token_response = session.post(
        f"{CREDENTIALS.base_url}/protocol/openid-connect/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": redirect_uri,
            "client_id": CREDENTIALS.client_id,
            "client_secret": CREDENTIALS.client_secret,
        },
    )
    if token_response.status_code != 200:
        raise RuntimeError(
            f"Token response was {token_response.status_code} expected 200"
        )
    return token_response.json()


def _get_token_data_from_machine_user():
    CREDENTIALS = get_credentials()
    aud = CREDENTIALS.base_url
    token_endpoint = aud + "/protocol/openid-connect/token"
    private_key = CREDENTIALS.private_key()

    claims = {
        "sub": CREDENTIALS.client_id,
        "iss": CREDENTIALS.client_id,
        "jti": str(uuid.uuid4()),
        "aud": aud,
        "exp": int(time()) + 300,  # 5mins in the future
    }

    additional_jwt_headers = {"kid": CREDENTIALS.key_id}
    client_assertion = jwt.encode(
        claims, private_key, algorithm="RS512", headers=additional_jwt_headers
    )
    token_response = requests.post(
        token_endpoint,
        data={
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": client_assertion,
        },
    )
    if token_response.status_code != 200:
        raise RuntimeError(
            f"Token response was {token_response.status_code} expected 200"
        )
    return token_response.json()