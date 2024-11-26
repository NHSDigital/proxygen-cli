import click
import toml
from pathlib import Path
from proxygen_cli.lib.settings import SETTINGS
from proxygen_cli.lib import proxygen_api, output
from proxygen_cli.cli import (
    command_credentials,
    command_settings,
    command_instance,
    command_spec,
    command_secret,
    command_docker,
    command_pytest_nhsd_apim_token,
)


# Fetch the version from pyproject.toml
def get_version():
    pyproject_path = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
    if pyproject_path.exists():
        pyproject = toml.load(pyproject_path)
        return pyproject.get("tool", {}).get("poetry", {}).get("version", "unknown")
    return "unknown"


@click.group()
def main():
    """Main group"""


@main.command()
def version():
    """Show the version of proxygen-cli."""
    click.echo(f"proxygen, version {get_version()}")


main.add_command(command_settings.settings)
main.add_command(command_credentials.credentials)
main.add_command(command_instance.instance)
main.add_command(command_spec.spec)
main.add_command(command_secret.secret)
main.add_command(command_docker.docker)
main.add_command(command_pytest_nhsd_apim_token.pytest_nhsd_apim)


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
