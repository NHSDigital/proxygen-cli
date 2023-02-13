import json

import click
import yaml

from proxygen_cli.lib import output
from proxygen_cli.lib.credentials import (
    Credentials,
    _yaml_credentials_file_source,
    get_credentials,
)
from proxygen_cli.lib.dot_proxygen import credentials_file

CHOICE_OF_CREDENTIAL_KEYS = click.Choice(Credentials.__fields__.keys())  # type: ignore[arg-type]


@click.group()
def credentials():
    """Get/set credentials."""


@credentials.command()
def list():
    """
    List all credentials values.
    """
    creds = get_credentials()
    output.print_spec(json.loads(creds.json(exclude_none=True)))


@credentials.command()
@click.argument("key", type=CHOICE_OF_CREDENTIAL_KEYS)
def get(key):
    """
    Read a value from your credentials.
    """
    creds = get_credentials()
    click.echo(getattr(creds, key))


@credentials.command()
@click.argument("key", type=CHOICE_OF_CREDENTIAL_KEYS)
@click.argument("value")
def set(key, value):
    """
    Write a value to your credentials.
    """
    current_credentials = _yaml_credentials_file_source(None)
    current_credentials[key] = value
    with credentials_file().open("w", encoding="utf-8") as f:
        yaml.safe_dump(current_credentials, f)


@credentials.command()
@click.argument("key", type=CHOICE_OF_CREDENTIAL_KEYS)
def rm(key):
    """
    Delete a value from your credentials.
    """
    current_credentials = _yaml_credentials_file_source(None)
    current_credentials.pop(key, None)
    with credentials_file().open("w", encoding="utf-8") as f:
        yaml.safe_dump(current_credentials, f)
