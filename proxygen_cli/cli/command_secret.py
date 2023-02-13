from typing import get_args

import click
from yaspin import yaspin

from proxygen_cli.lib import output, proxygen_api, version
from proxygen_cli.lib.constants import LITERAL_ENVS
from proxygen_cli.lib.settings import SETTINGS

CHOICE_OF_ENVS = click.Choice(get_args(LITERAL_ENVS))


@click.group()
@click.option("--api", default=SETTINGS.api, help="Override the default API", show_default=True)
@click.pass_context
def secret(ctx, api):
    """
    Create/Update/Delete secrets used by your API.
    """
    version.validate_cli_version()
    ctx.ensure_object(dict)
    ctx.obj["api"] = api
    if api is None:
        raise click.UsageError("You must set the API before using this command: see `proxygen settings`")


@secret.command()
@click.pass_context
@click.option("--env", type=CHOICE_OF_ENVS, help="Only print secrets in the choice environment.")
def list(ctx, env):
    """
    List secrets.

    Optionally just in the specified environment.
    """
    api = ctx.obj["api"]
    if env:
        result = proxygen_api.get_secrets(api, env)
    else:
        result = proxygen_api.get_resources(api, _type="secret")
    output.print_table(result)


@secret.command()
@click.argument("env", type=CHOICE_OF_ENVS)
@click.argument("secret_name")
@click.option("--secret-value")
@click.option("--secret-file")
@click.option("--apikey", is_flag=True, help="Tag this secret as an apikey")
@click.pass_context
def put(ctx, env, secret_name, secret_value, secret_file, apikey):
    # pylint: disable=too-many-arguments
    """
    Create or overwrite a secret.

    This command makes the secret available to your instances.
    """
    if secret_value is None and secret_file is None:
        raise click.UsageError("Please specify one of --secret-value and --secret-file.")
    if secret_value is not None and secret_file is not None:
        raise click.UsageError("Please specify one of --secret-value and --secret-file, not both.")
    if secret_file is not None:
        try:
            with open(secret_file, "r", encoding="utf-8") as _file:
                secret_value = _file.read()
        except FileNotFoundError as e:
            raise ValueError(f"Cannot find secret file {secret_file}.") from e

    api = ctx.obj["api"]
    _type = None
    if apikey:
        _type = "apikey"

    with yaspin() as spin:
        spin.text = f"Putting secret {secret_name} in {env}"
        result = proxygen_api.put_secret(api, env, secret_name, secret_value, _type=_type)
        spin.ok("✔")

    output.print_json(result)


@secret.command()
@click.argument("env", type=CHOICE_OF_ENVS)
@click.argument("secret_name")
@click.pass_context
def describe(ctx, env, secret_name):
    """
    Describe a secret.
    """
    api = ctx.obj["api"]
    result = proxygen_api.get_secret(api, env, secret_name)
    output.print_json(result)


@secret.command()
@click.argument("env", type=CHOICE_OF_ENVS)
@click.argument("secret_name")
@click.option("--no-confirm", is_flag=True, show_default=True, help="Do not prompt for confirmation.")
@click.pass_context
def delete(ctx, env, secret_name, no_confirm):
    """
    Delete a secret.
    """
    api = ctx.obj["api"]

    if not no_confirm:
        result = proxygen_api.get_secret(api, env, secret_name)
        if result is None:
            raise click.BadArgumentUsage(f"A secret named {secret_name} does not exist in {env}.")
        output.print_json(result)
        if not click.confirm(f"Delete secret {secret_name} from {env}?"):
            raise click.Abort()
    with yaspin() as spin:
        spin.text = f"Deleting secret {secret_name} from {env}"
        result = proxygen_api.delete_secret(api, env, secret_name)
        spin.ok("✔")
