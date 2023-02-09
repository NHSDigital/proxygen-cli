import click

from proxygen_cli.lib.settings import SETTINGS
from proxygen_cli.lib import output, proxygen_api, spec, version


@click.group()
@click.option(
    "--api", default=SETTINGS.api, help="Override the default API", show_default=True
)
@click.pass_context
def docker(ctx, api):
    """
    Interact with your API's docker repository
    """
    version.validate_cli_version()
    ctx.ensure_object(dict)
    ctx.obj["api"] = api
    if api is None:
        raise click.UsageError("You must set the API before using this command: see `proxygen settings`")


@docker.command()
@click.pass_context
def get_login(ctx):
    """
    Generate docker login command for AWS ECR repo with credentials from proxygen.
    """
    api = ctx.obj["api"]
    resp = proxygen_api.get_docker_login(api)
    click.echo(f"docker login -u {resp['user']} --password {resp['password']} {resp['registry']}")



@docker.command()
@click.pass_context
def registry(ctx):
    """
    Print the AWS registry.
    """
    api = ctx.obj["api"]
    resp = proxygen_api.get_docker_login(api)
    registry_url = resp["registry"]
    # Strip leading https://
    click.echo(registry_url[8:])
