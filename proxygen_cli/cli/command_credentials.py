import json
import yaml
import click

from proxygen_cli.lib import output
from proxygen_cli.lib.credentials import CREDENTIALS, _yaml_credentials_file_source
from proxygen_cli.lib.dot_proxygen import credentials_file

CHOICE_OF_CREDENTIAL_KEYS = click.Choice(CREDENTIALS.__dict__.keys())


@click.group()
def credentials():
    """Get/set credentials."""
    pass


def _get_setting(key):
    return getattr(CREDENTIALS, key)

@credentials.command()
def list():
    """
    List all credentials values.
    """
    output.print_spec(json.loads(CREDENTIALS.json(exclude_none=True)))

@credentials.command()
@click.argument("key", type=CHOICE_OF_CREDENTIAL_KEYS)
def get(key):
    """
    Read a value from your credentials.
    """
    click.echo(_get_setting(key))


@credentials.command()
@click.argument("key", type=CHOICE_OF_CREDENTIAL_KEYS)
@click.argument("value")
def set(key, value):
    """
    Write a value to your credentials.
    """
    _get_setting(key)

    current_credentials = _yaml_credentials_file_source(None)
    current_credentials[key] = value
    try:
        new_credentials = json.loads(CREDENTIALS(**current_credentials).json(exclude_none=True))
    except pydantic.ValidationError as e:
        errors = json.loads(e.json())
        raise click.BadParameter("\n".join(error["msg"] for error in errors))
    with credentials_file().open("w") as f:
        yaml.safe_dump(new_credentials, f)


@credentials.command()
@click.argument("key", type=CHOICE_OF_CREDENTIAL_KEYS)
def rm(key):
    """
    Delete a value from your credentials.
    """
    _get_setting(key)

    current_credentials = _yaml_credentials_file_source(None)
    current_credentials.pop(key, None)
    with credentials_file().open("w") as f:
        yaml.safe_dump(current_credentials, f)
