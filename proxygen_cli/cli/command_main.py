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
)


@click.group()
def main():
    version.validate_cli_version()


main.add_command(command_settings.settings)
main.add_command(command_credentials.credentials)
main.add_command(command_instance.instance)
main.add_command(command_spec.spec_cmd, name="spec")
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


@main.command()
@click.option(
    "--api", default=SETTINGS.api, help="Override the default API", show_default=True
)
def docker_get_login(api):
    """
    Generate docker login command for AWS ECR repo with credentials from proxygen.
    """
    resp = proxygen_api.get_docker_login(api)
    click.echo(f"docker login -u {resp['user']} --password {resp['password']} {resp['registry']}")


if __name__ == "__main__":
    main()
