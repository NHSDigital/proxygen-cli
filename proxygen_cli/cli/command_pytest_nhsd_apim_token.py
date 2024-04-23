import click

from proxygen_cli.lib.settings import SETTINGS
from proxygen_cli.lib import proxygen_api, version, output


@click.group()
@click.option(
    "--api", default=SETTINGS.api, help="Override the default API", show_default=True
)
@click.pass_context
def pytest_nhsd_apim(ctx, api):
    """
    Intract with your API's pytest_nhsd_apim assets
    """
    version.validate_cli_version()
    ctx.ensure_object(dict)
    if api is None:
        raise click.UsageError(
            "You must set the API before using this command: see `proxygen settings`"
        )
    ctx.obj["api"] = api


@pytest_nhsd_apim.command()
@click.pass_context
def get_token(ctx):
    """
    Get a token for use with pytest-nhsd-apim python testing package.
    """
    api = ctx.obj["api"]
    resp = proxygen_api.get_pytest_nhsd_apim_token(api)
    output.print_json(resp)
