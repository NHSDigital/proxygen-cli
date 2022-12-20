import sys
from typing import get_args
from urllib import parse
import click

from proxygen_cli.lib import constants, proxygen_api, settings, output, version
from proxygen_cli.cli import (
    command_credentials,
    command_settings,
    command_instance,
    command_secret,
)


@click.group()
def main():
    version.validate_cli_version()


main.add_command(command_settings.settings)
main.add_command(command_credentials.credentials)
main.add_command(command_instance.instance)
main.add_command(command_secret.secret)


@main.command()
def status():
    """
    Query the proxygen service status endpoint.
    """
    status = proxygen_api.status()
    output.print_json(
        {"proxygen_url": str(settings.SETTINGS.endpoint_url), "response": status}
    )


if __name__ == "__main__":
    main()
