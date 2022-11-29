from typing import get_args
from urllib import parse

import click

from proxygen_cli.lib import output, proxygen_api, spec
from proxygen_cli.lib.settings import SETTINGS
from proxygen_cli.lib.constants import LITERAL_ENVS

CHOICE_OF_ENVS = click.Choice(get_args(LITERAL_ENVS))


@click.group()
@click.option(
    "--api", default=SETTINGS.api, help="Override the default API", show_default=True
)
@click.pass_context
def secret(ctx, api):
    ctx.ensure_object(dict)
    ctx.obj["api"] = api


@secret.command()
@click.pass_context
@click.option(
    "--env", type=CHOICE_OF_ENVS, help="Only print secrets in the choice environment."
)
def list(ctx, env):
    """
    List secrets.

    Optionally just in the specified environment.
    """
    api = ctx.obj["api"]

    if env:
        result = {
            "environments": {
                env: proxygen_api.get_api_environment(api, env)
            }
        }
    else:
        result = proxygen_api.get_api(api)

    objects = []
    for env in result["environments"]:
        secrets = result["environments"][env]["secrets"]
        for secret in secrets:
            objects.append({"environment": env, **secret})
    output.print_table(objects)


@secret.command()
@click.argument("env", type=CHOICE_OF_ENVS)
@click.argument("secret_name")
@click.option("--secret-value")
@click.option("--secret-file")
@click.option("--apikey", is_flag=True, help="Tag this secret as an apikey")
@click.pass_context
def put(ctx, env, secret_name, secret_value, secret_file, apikey):
    """
    Make a secret available to your instances.

    
    """
    if secret_value is None and secret_file is None:
        raise ValueError("Please specify one of --secret-value and --secret-file.")
    if secret_value is not None and secret_file is not None:
        raise ValueError("Please specify one of --secret-value and --secret-file, not both.")
    elif secret_file is not None:
        try:
            with open(secret_file) as f:
                secret_value = f.read()
        except FileNotFoundError:
            raise ValueError(f"Cannot find secret file {secret_file}.")

    api = ctx.obj["api"]
    _type = None
    if apikey:
        _type = "apikey"
    
    result = proxygen_api.put_secret(api, env, secret_name, secret_value, _type=_type)
    output.print_json(result)


@secret.command()
@click.argument("env", type=CHOICE_OF_ENVS)
@click.argument("secret_name")
@click.pass_context
def describe(ctx, env, secret_name):
    """
    Get the spec used to deploy the secret in environment <ENV> with base path <NAME>.
    """
    api = ctx.obj["api"]
    result = proxygen_api.get_secret(api, env, secret_name)
    output.print_json(result)
    

@secret.command()
@click.argument("env", type=CHOICE_OF_ENVS)
@click.argument("secret_name")
@click.option(
    "--no-confirm", is_flag=True, show_default=True, help="Do not prompt for confirmation."
)
@click.pass_context
def delete(ctx, env, secret_name, no_confirm):
    """
    Delete the secret called <NAME> in environment <ENV>.
    """
    api = ctx.obj["api"]

    if not no_confirm:
        result = proxygen_api.get_secret(api, env, secret_name)
        output.print_json(result)
        if not click.confirm(f"Delete secret {secret_name} from {env}?"):
            raise click.Abort()
    
    result = proxygen_api.delete_secret(api, env, secret_name)
    output.print_json(result)
