import yaml
import click

from proxygen_cli.lib.settings import SETTINGS, _yaml_settings_file_source
from proxygen_cli.lib.dot_proxygen import settings_file


@click.group()
def settings():
    pass


def _get_setting(key):
    try:
        return getattr(SETTINGS, key)
    except AttributeError as e:
        raise ValueError(f"No such setting: {key}")

@settings.command()
@click.argument("key")
def get(key):
    """
    Read a value from your settings.
    """
    click.echo(_get_setting(key))
    
@settings.command()
@click.argument("key")
@click.argument("value")
def set(key, value):
    """
    Write a value to your settings.
    """
    _get_setting(key)

    current_settings = _yaml_settings_file_source(None)
    current_settings[key] = value
    with settings_file().open("w") as f:
        yaml.safe_dump(current_settings, f)


@settings.command()
@click.argument("key")
def rm(key):
    """
    Delete a value from your settings.
    """
    _get_setting(key)
    
    current_settings = _yaml_settings_file_source(None)
    current_settings.pop(key)
    with settings_file().open("w") as f:
        yaml.safe_dumps(current_settings, f)
