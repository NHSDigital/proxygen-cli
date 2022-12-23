from typing import get_args

import click
from yaspin import yaspin

from proxygen_cli.lib import output, proxygen_api, spec
from proxygen_cli.lib.settings import SETTINGS
from proxygen_cli.lib.constants import LITERAL_ENVS

CHOICE_OF_ENVS = click.Choice(get_args(LITERAL_ENVS))


@click.group()
@click.option(
    "--api", default=SETTINGS.api, help="Override the default API", show_default=True
)
@click.pass_context
def spec_cmd(ctx, api):
    ctx.ensure_object(dict)
    ctx.obj["api"] = api


@spec_cmd.command()
@click.argument("env", type=CHOICE_OF_ENVS)
@click.argument("base_path")
@click.argument("spec_file")
@click.option(
    "--no-confirm",
    is_flag=True,
    show_default=True,
    help="Do not prompt for confirmation.",
)
@click.pass_context
def publish(ctx, env, base_path, spec_file, no_confirm):
    """
    Publish <SPEC_FILE>, rendered with <ENV> and <BASE_PATH>

    Your spec is published under <API>.
    """

    api = ctx.obj["api"]
    paas_open_api = spec.resolve(spec_file, api, env, base_path)

    if not no_confirm:
        output.print_spec(paas_open_api)
        if not click.confirm(f"Deploy this spec for {api}?"):
            raise click.Abort()

    with yaspin() as sp:
        sp.text = f"Releasing spec {api}"
        proxygen_api.put_spec(api, paas_open_api)
        sp.ok("✔")


@spec_cmd.command()
@click.pass_context
def get(ctx):
    """
    Get the API published spec.
    """
    api = ctx.obj["api"]
    result = proxygen_api.get_spec(api)
    output.print_spec(result)


@spec_cmd.command()
@click.option(
    "--no-confirm",
    is_flag=True,
    show_default=True,
    help="Do not prompt for confirmation.",
)
@click.pass_context
def delete(ctx, no_confirm):
    """
    Delete the published spec.
    """
    api = ctx.obj["api"]
    if not no_confirm:
        result = proxygen_api.get_spec(api)
        if not result:
            raise click.ClickException(f"No such spec under {api}")
        output.print_spec(result)
        if not click.confirm(f"Delete the spec at {api}?"):
            raise click.Abort()

    with yaspin() as sp:
        sp.text = f"Deleting spec {api}"
        result = proxygen_api.delete_spec(api)
        sp.ok("✔")
