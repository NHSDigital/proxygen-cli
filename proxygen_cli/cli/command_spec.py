from typing import get_args

import click
from yaspin import yaspin

from proxygen_cli.lib import output, proxygen_api, spec, spec_server
from proxygen_cli.lib.constants import LITERAL_ENVS
from proxygen_cli.lib.settings import SETTINGS

CHOICE_OF_ENVS = click.Choice(get_args(LITERAL_ENVS))
PUBLISH_SPEC_POP_KEYS = ["x-nhsd-apim"]  # Don't publish deployment information


@click.group()
@click.option(
    "--api", default=SETTINGS.api, help="Override the default API", show_default=True
)
@click.pass_context
def spec_cmd(ctx, api):
    ctx.ensure_object(dict)
    ctx.obj["api"] = api


@spec_cmd.command()
@click.argument("spec_file")
@click.option(
    "--no-confirm",
    is_flag=True,
    show_default=True,
    help="Do not prompt for confirmation.",
)
@click.option(
    "--uat", default=False, help="Spec for UAT environment", is_flag=True
)
@click.pass_context
def publish(ctx, spec_file, no_confirm, uat):
    """
    Publish <SPEC_FILE>.
    """

    api = ctx.obj["api"]
    paas_open_api = spec.resolve(spec_file, pop_keys=PUBLISH_SPEC_POP_KEYS)

    if not no_confirm:
        output.print_spec(paas_open_api)
        if not click.confirm(f"Publish this spec for {api}?"):
            raise click.Abort()

    with yaspin() as sp:
        sp.text = f"Publishing spec {api}"
        proxygen_api.put_spec(api, paas_open_api, uat)
        sp.ok("✔")


@click.command()
@click.argument("spec_file")
def serve(spec_file):
    """
    Serve API spec in <spec_file> locally on port 8008.
    """
    print(f"""
    Serving {spec_file} on port 8008.
    To preview go to "https://editor.swagger.io".
    Click "File -> Import URL".
    Provide the location "http://localhost:8008".

    Note that any edits you make here will *NOT* be propagated back to {spec_file}.
    """)
    spec_server.serve(spec_file, pop_keys=PUBLISH_SPEC_POP_KEYS)


@spec_cmd.command()
@click.option(
    "--uat", default=False, help="Spec for UAT environment", is_flag=True
)
@click.pass_context
def get(ctx, uat):
    """
    Get the API published spec.
    """
    api = ctx.obj["api"]
    result = proxygen_api.get_spec(api, uat)
    output.print_spec(result)


@spec_cmd.command()
@click.option(
    "--no-confirm",
    is_flag=True,
    show_default=True,
    help="Do not prompt for confirmation.",
)
@click.option(
    "--uat", default=False, help="Spec for UAT environment", is_flag=True
)
@click.pass_context
def delete(ctx, no_confirm, uat):
    """
    Delete the published spec.
    """
    api = ctx.obj["api"]
    if not no_confirm:
        result = proxygen_api.get_spec(api, uat)
        if not result:
            raise click.ClickException(f"No such spec under {api}")
        output.print_spec(result)
        if not click.confirm(f"Delete the spec at {api}?"):
            raise click.Abort()

    with yaspin() as sp:
        sp.text = f"Deleting spec {api}"
        result = proxygen_api.delete_spec(api, uat)
        sp.ok("✔")
