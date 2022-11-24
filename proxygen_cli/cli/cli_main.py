import sys
from typing import get_args
from urllib import parse

import click

from proxygen_cli.lib import constants, proxygen_api, output, settings
from proxygen_cli.cli import cli_credentials, cli_settings


@click.group()
def main():
    pass

main.add_command(cli_settings.settings)
main.add_command(cli_credentials.credentials)

@main.command()
def status():
    """
    Query the proxygen service status endpoint.
    """
    status = proxygen_api.status()
    output.print_json({"proxygen_url": str(settings.SETTINGS.endpoint_url), "response": status})


@main.command()
@click.option("--api")
@click.option("--environment", type=click.Choice(get_args(constants.LITERAL_ENVS)))
def ls(api, environment):
    """
    List items, optionally filter by environment.
    """

    if not environment:
        result = proxygen_api.get_api(api)            
        
    if environment:
        result = {"environments": {environment: proxygen_api.get_api_environment(api, environment)}}

    # objects = []    
    # for env in result["environments"]:
    #     instances = result["environments"][env]["instances"]
    #     secrets = result["environments"][env]["secrets"]

    #     for instance in instances:
    #         objects.append({"type": "instance", "name": instance, "environment": env})
    #     for secret in secrets:
    #         objects.append({"type": "secret", "name": instance, "environment": env})
                
    # cli_output.output(objects)
    cli_output.output(result)


def required(ctx, param, value):
    if value is None:
        raise ValueError(f"Option {param.opts[0]} is required")
    return value









@main.group()
def instance():
    """Create/Update/Delete instances."""
    pass


@instance.command()
@click.option("--api", callback=required)
@click.option(
    "--environment",
    type=click.Choice(get_args(constants.LITERAL_ENVS)),
    callback=required,
)
@click.option("--path", callback=required)
def describe(api, environment, path):
    """Get the OpenAPISpec from which the instance was generated."""
    instance = parse.quote(path)
    result = proxygen_api.get_instance(api, environment, instance)
    cli_output.output(result)

@instance.command()
@click.option("--api", callback=required)
@click.option(
    "--environment",
    type=click.Choice(get_args(constants.LITERAL_ENVS)),
    callback=required,
)
@click.option("--path", callback=required)
def rm(api, environment, path):
    """Delete the instance."""
    instance = parse.quote(path)
    result = proxygen_api.delete_instance(api, environment, instance)
    cli_output.output(result)

@instance.command()
@click.option("--api", callback=required)
@click.option("--environment", callback=required)
@click.option("--path", callback=required)
@click.option("--spec-file", callback=required)
def deploy(api, environment, path, spec_file):
    """Deploy an instance from a spec file."""

    paas_open_api = spec.resolve(spec_file)

    # Overwrite the servers object to point to the values provided form the cli
    sub_domain = "api" if environment == "prod" else f"{environment}.api"
    paas_open_api["servers"] = [
        {"url": f"https://{sub_domain}.service.nhs.uk/{path}"}
    ]

    instance = parse.quote(path)
    result = proxygen_api.put_instance(api, environment, instance, paas_open_api)
    cli_output.output(result)
















@main.group()
def secret():
    """Create/Update/Delete secrets."""
    pass


@secret.command()
@click.option("--api", callback=required)
@click.option(
    "--environment",
    type=click.Choice(get_args(constants.LITERAL_ENVS)),
    callback=required,
)
@click.option("--secret", callback=required)
def describe(api, environment, secret):
    """Describe a secret"""
    result = proxygen_api.get_secret(api, environment, secret)
    cli_output.output(result)

@secret.command()
@click.option("--api", callback=required)
@click.option(
    "--environment",
    type=click.Choice(get_args(constants.LITERAL_ENVS)),
    callback=required,
)
@click.option("--secret", callback=required)
def describe(api, environment, secret):
    """Describe a secret"""

    result = proxygen_api.get_secret(api, environment, secret)
    cli_output.output(result)


@secret.command()
@click.option("--api", callback=required)
@click.option(
    "--environment",
    type=click.Choice(get_args(constants.LITERAL_ENVS)),
    callback=required,
)
@click.option("--secret", callback=required)
def rm(api, environment, secret):
    """Delete a secret"""

    result = proxygen_api.delete_secret(api, environment, secret)
    cli_output.output(result)


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        click.echo(e, err=True)
        sys.exit(1)
