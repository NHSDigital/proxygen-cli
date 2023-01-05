import json
import yaml
import click
import pydantic

from proxygen_cli.lib import output
from proxygen_cli.lib.settings import SETTINGS, Settings, _yaml_settings_file_source
from proxygen_cli.lib.dot_proxygen import settings_file

CHOICE_OF_SETTINGS_KEYS = click.Choice(Settings.__fields__.keys())


@click.group()
def settings():
    """
    Get/set settings for the proxygen-cli.
    """
    pass


def _get_setting(key):
    try:
        return getattr(SETTINGS, key)
    except AttributeError as e:
        raise ValueError(f"No such setting: {key}")


@settings.command()
def list():
    """
    List all settings values.
    """
    output.print_spec(json.loads(SETTINGS.json(exclude_none=True)))

@settings.command()
@click.argument("key", type=CHOICE_OF_SETTINGS_KEYS)
def get(key):
    """
    Read a value from your settings.
    """
    click.echo(_get_setting(key))

    
@settings.command()
@click.argument("key", type=CHOICE_OF_SETTINGS_KEYS)
@click.argument("value")
def set(key, value):
    """
    Write a value to your settings.
    """
    _get_setting(key)

    current_settings = _yaml_settings_file_source(None)
    current_settings[key] = value
    try:
        new_settings = json.loads(Settings(**current_settings).json(exclude_none=True))
    except pydantic.ValidationError as e:
        errors = json.loads(e.json())
        raise click.BadParameter("\n".join(error["msg"] for error in errors))
    with settings_file().open("w") as f:
        yaml.safe_dump(new_settings, f)


@settings.command()
@click.argument("key", type=CHOICE_OF_SETTINGS_KEYS)
def rm(key):
    """
    Delete a value from your settings.
    """
    _get_setting(key)
    
    current_settings = _yaml_settings_file_source(None)
    current_settings.pop(key, None)
    with settings_file().open("w") as f:
        yaml.safe_dump(current_settings, f)
