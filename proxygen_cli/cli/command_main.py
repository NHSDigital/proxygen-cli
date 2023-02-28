import sys
from typing import get_args
from urllib import parse
import click
from proxygen_cli.lib.settings import SETTINGS

from proxygen_cli.lib import constants, proxygen_api, settings, output, version
from proxygen_cli.cli import (
    command_credentials,
    command_settings,
    command_instance,
    command_spec,
    command_secret,
    command_docker,
)


@click.group()
def main():
    """Main group"""


main.add_command(command_settings.settings)
main.add_command(command_credentials.credentials)
main.add_command(command_instance.instance)
main.add_command(command_spec.spec_cmd, name="spec")
main.add_command(command_secret.secret)
main.add_command(command_docker.docker)


@main.command()
def status():
    """
    Query the proxygen service status endpoint.
    """
    status = proxygen_api.status()
    output.print_json(
        {"proxygen_url": str(SETTINGS.endpoint_url), "response": status}
    )


if __name__ == "__main__":
    main()
