from typing import Optional, Literal
from configparser import ConfigParser
from dataclasses import dataclass, asdict
import json
import hashlib

from . import dot_proxygen


def cache_key(client, user):
    s = json.dumps({"client": asdict(client), "user": asdict(user)})
    return hashlib.md5(s.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ClientCredentials:
    name: str
    id: str
    secret: str
    base_url: Optional[str] = None


@dataclass(frozen=True)
class UserCredentials:
    name: str
    password: str


@dataclass(frozen=True)
class MachineCredentials:
    name: str
    private_key_path: str

    def private_key(self):
        private_key_file = dot_proxygen.credentials_file().joinpath(self.private_key_path)
        if not private_key_file.exists():
            raise ValueError(f"Could not open private key file {private_key_file} for machine user {self.name}")
        with private_key_file.open() as f:
            return f.read()


def _select_default(
    items,
    default_name: Optional[str],
    cred_type: Literal["user", "machine"],
    cred_file_name,
    config_file_name,
):

    if default_name is not None:
        matching_items = list(filter(lambda item: item.name == default_name, items))
        if len(matching_items) == 0:
            raise ValueError(
                f"No credentials for [{cred_type} {default_name}] in {cred_file_name}"
            )
        else:
            return matching_items[0]

    # There is no default name
    if len(items) == 1:
        return items[0]

    if len(items) == 0:
        raise ValueError(f"No credentials for [{cred_type} *****] in {cred_file_name}")

    raise ValueError(
        f"Please specify which {cred_type} in {config_file_name} section [default], e.g.\nsection[default]\n{cred_type} = MY_CHOSEN_{cred_type.upper()}"
    )


def read_credentials():
    config_file_name = str(dot_proxygen.config_file())
    config = ConfigParser()
    config.read(config_file_name)

    credentials_file_name = str(dot_proxygen.credentials_file())
    credentials = ConfigParser()
    credentials.read(credentials_file_name)

    clients = []
    users = []
    for section in credentials.sections():
        section_dict = {k: v for k, v in credentials[section].items()}
        if section.startswith("client "):
            client = ClientCredentials(**section_dict, name=section[7:])
            clients.append(client)
        elif section.startswith("user "):
            user = None
            for cls in [UserCredentials, MachineCredentials]:
                try:
                    user = cls(**section_dict, name=section[5:])
                except TypeError as e:
                    pass
            if user is None:
                raise TypeError(
                    f"Unable to parse {credentials_file_name} section [{section}] as user credentials or machine credentials."
                )
            users.append(user)

    defaults = config["default"] if "default" in config.sections() else {}

    selected_client = _select_default(
        clients,
        defaults.get("client"),
        "client",
        credentials_file_name,
        config_file_name,
    )
    selected_user = _select_default(
        users, defaults.get("user"), "user", credentials_file_name, config_file_name
    )
    return selected_client, selected_user
