import sys
from typing import get_args

import click

from proxygen_cli import cli_output, proxygen_api, constants, config, spec


@click.group()
def main():
    pass


@main.command()
def status():
    """
    Query the proxygen service status endpoint.
    """
    cfg = config.set_api_config(None)
    status = proxygen_api.status()

    cli_output.output({"proxygen_url": str(cfg.endpoint_url), "response": status})


@main.command()
@click.option("--api")
@click.option("--environment", type=click.Choice(get_args(constants.LITERAL_ENVS)))
def ls(api, environment):
    """
    List items, optionally filter by environment.
    """
    config.set_api_config(api)

    if not environment:
        result = proxygen_api.get_api(api)
    if environment:
        result = proxygen_api.get_api_environment(api, environment)

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
@click.option("--instance", callback=required)
def describe(api, environment, instance):
    """Get the OpenAPISpec from which the instance was generated."""
    config.set_api_config(api)
    result = proxygen_api.get_instance(api, environment, instance)
    cli_output.output(result)

@instance.command()
@click.option("--api", callback=required)
@click.option(
    "--environment",
    type=click.Choice(get_args(constants.LITERAL_ENVS)),
    callback=required,
)
@click.option("--instance", callback=required)
def rm(api, environment, instance):
    """Delete the instance."""
    config.set_api_config(api)
    result = proxygen_api.delete_instance(api, environment, instance)
    cli_output.output(result)

@instance.command()
@click.option("--api", callback=required)
@click.option("--environment", callback=required)
@click.option("--base-path", callback=required)
@click.option("--spec-file", callback=required)
def deploy(api, environment, base_path, spec_file):
    """Deploy an instance from a spec file."""

    config.set_api_config(api)

    paas_open_api = spec.resolve(spec_file)

    # Overwrite the servers object to point to the values provided form the cli
    sub_domain = "api" if environment == "prod" else f"{environment}.api"
    paas_open_api["servers"] = [
        {"url": f"https://{sub_domain}.service.nhs.uk/{base_path}"}
    ]
    instance = base_path.replace("/","_")

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
    config.set_api_config(api)

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
    config.set_api_config(api)

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
    config.set_api_config(api)

    result = proxygen_api.delete_secret(api, environment, secret)
    cli_output.output(result)


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        click.echo(e, err=True)
        sys.exit(1)
