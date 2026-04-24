import json
import click
import yaml
import pydantic
import os

from proxygen_cli.lib import output
from proxygen_cli.lib.credentials import (
    Credentials, get_credentials, _yaml_credentials_file_source, create_yaml_credentials_file, initialise_credentials)
from proxygen_cli.lib.dot_proxygen import credentials_file

CHOICE_OF_CREDENTIAL_KEYS = click.Choice(Credentials.__fields__.keys())

@click.group()
def credentials():
    """Get/set credentials."""


@credentials.command()
def list():
    """
    List all credentials values.
    """
    if not _yaml_credentials_file_source(None):
        click.echo("Credentials file does not exist. Please run 'proxygen credentials set'")
        exit()

    creds = get_credentials()
    output.print_spec(json.loads(creds.json(exclude_none=True)))


@credentials.command()
@click.argument("key", type=CHOICE_OF_CREDENTIAL_KEYS)
def get(key):
    """
    Read a value from your credentials.
    """
    if not _yaml_credentials_file_source(None):
        click.echo("Credentials file does not exist. Please run 'proxygen credentials set'")
        exit()

    creds = get_credentials()
    click.echo(getattr(creds, key))

@credentials.command()
@click.argument("custom_pairs", nargs=-1, metavar="KEY VALUE", required=False)
@click.option("--force", is_flag=True, help="Force re-entry of standard credentials")
@click.option("--env", type=click.Choice(["prod", "ptl"], case_sensitive=False), default="prod", help="Environment to use for authentication")
def set(custom_pairs, force, env):
    """
    Write a value to your credentials.
    """
    if not _yaml_credentials_file_source(None):
        create_yaml_credentials_file()

    current_credentials = _yaml_credentials_file_source(None)

    #current_credentials["env"] = env.lower()

    KEYCLOAK_URLS = {
        "prod": "https://identity.prod.api.platform.nhs.uk/realms/api-producers",
        "ptl":  "https://identity.ptl.api.platform.nhs.uk/realms/api-producers",
    }

    current_credentials["base_url"] = KEYCLOAK_URLS[env.lower()]

    context = click.get_current_context()
    if ("private_key_path" not in context.params["custom_pairs"]):
        clientID = click.prompt("Enter client ID", default="", show_default=False)
        clientSecret = click.prompt("Enter client secret", default="", show_default=False)
        username = click.prompt("Enter username", default="", show_default=False)
        password = click.prompt("Enter password", default="", show_default=False)

        current_credentials["client_id"] = clientID
        current_credentials["client_secret"] = clientSecret
        current_credentials["username"] = username
        current_credentials["password"] = password

    # Prompt for individual custom key-value pairs
    for i in range(0, len(custom_pairs), 2):
        key, value = custom_pairs[i:i + 2]
        current_credentials[key] = value

    try:
        new_credentials = json.loads(Credentials(**current_credentials).json(exclude_none=True))
    except pydantic.ValidationError as e:
        errors = json.loads(e.json())
        raise click.BadParameter("\n".join(error["msg"] for error in errors))

    with credentials_file().open("w") as f:
        yaml.safe_dump(new_credentials, f)

    initialise_credentials()


@credentials.command()
@click.argument("key", type=CHOICE_OF_CREDENTIAL_KEYS)
def rm(key):
    """
    Delete a value from your credentials.
    """
    current_credentials = _yaml_credentials_file_source(None)
    current_credentials.pop(key, None)
    with credentials_file().open("w") as f:
        yaml.safe_dump(current_credentials, f)