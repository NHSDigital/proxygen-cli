import yaml
import click

from proxygen_cli.lib.credentials import CREDENTIALS, _yaml_credentials_file_source
from proxygen_cli.lib.dot_proxygen import credentials_file


@click.group()
def credentials():
    pass


def _get_setting(key):
    try:
        return getattr(CREDENTIALS, key)
    except AttributeError as e:
        raise ValueError(f"No such setting: {key}")


@credentials.command()
@click.argument("key")
def get(key):
    """
    Read a value from your credentials.
    """
    click.echo(_get_setting(key))


@credentials.command()
@click.argument("key")
@click.argument("value")
def set(key, value):
    """
    Write a value to your credentials.
    """
    _get_setting(key)

    current_credentials = _yaml_credentials_file_source(None)
    current_credentials[key] = value
    with credentials_file().open("w") as f:
        yaml.safe_dump(current_credentials, f)


@credentials.command()
@click.argument("key")
def rm(key):
    """
    Delete a value from your credentials.
    """
    _get_setting(key)

    current_credentials = _yaml_credentials_file_source(None)
    current_credentials.pop(key)
    with credentials_file().open("w") as f:
        yaml.safe_dumps(current_credentials, f)
