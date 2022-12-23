from typing import get_args
from urllib import parse

import click
from yaspin import yaspin
from tabulate import tabulate

from proxygen_cli.lib import output, proxygen_api, spec
from proxygen_cli.lib.settings import SETTINGS
from proxygen_cli.lib.constants import LITERAL_ENVS

CHOICE_OF_ENVS = click.Choice(get_args(LITERAL_ENVS))


@click.group()
@click.option(
    "--api", default=SETTINGS.api, help="Override the default API", show_default=True
)
@click.pass_context
def instance(ctx, api):
    ctx.ensure_object(dict)
    ctx.obj["api"] = api


@instance.command()
@click.pass_context
@click.option(
    "--env", type=CHOICE_OF_ENVS, help="Only print instances in the choice environment."
)
def list(ctx, env):
    api = ctx.obj["api"]

    if env:
        objects = proxygen_api.get_instances(api, env)
    else:
        objects = proxygen_api.get_resources(api, _type="instance")
    output.print_table(objects)


@instance.command()
@click.argument("env", type=CHOICE_OF_ENVS)
@click.argument("base_path")
@click.argument("spec_file")
@click.option(
    "--no-confirm", is_flag=True, show_default=True, help="Do not prompt for confirmation."
)
@click.pass_context
def deploy(ctx, env, base_path, spec_file, no_confirm):
    """
    Deploy <SPEC_FILE> to <ENV> under <BASE_PATH>

    Your instance is deployed at
    https://<ENV>.api.service.nhs.uk/<BASE_PATH> unless <ENV> is
    "prod", then it is deployed to
    https://api.service.nhs.uk/<BASE_PATH>.
    """
    
    api = ctx.obj["api"]
    paas_open_api = spec.resolve(spec_file, api, env, base_path)

    # Overwrite the servers object to point to the values provided from the cli
    _url = spec.url(env, base_path)
    paas_open_api["servers"] = [{"url": _url}]

    if not no_confirm:
        output.print_spec(paas_open_api)
        if not click.confirm(f"Deploy this spec to {_url}?"):
            raise click.Abort()

    with yaspin() as sp:
        sp.text = f"Deploying {_url}"
        instance = parse.quote(base_path)
        result = proxygen_api.put_instance(api, env, instance, paas_open_api)
        sp.ok("✔")
@instance.command()
@click.argument("env", type=CHOICE_OF_ENVS)
@click.argument("base_path")
@click.pass_context
def get(ctx, env, base_path):
    """
    Get the spec used to deploy the instance in environment <ENV> with base path <BASE_PATH>.
    """
    api = ctx.obj["api"]
    instance = parse.quote(base_path)
    result = proxygen_api.get_instance(api, env, instance)
    output.print_spec(result)
    

@instance.command()
@click.argument("env", type=CHOICE_OF_ENVS)
@click.argument("base_path")
@click.option(
    "--no-confirm", is_flag=True, show_default=True, help="Do not prompt for confirmation."
)
@click.pass_context
def delete(ctx, env, base_path, no_confirm):
    """
    Delete the instance deployed on <BASE_PATH> in environment <ENV>.
    """
    api = ctx.obj["api"]
    instance = parse.quote(base_path)
    _url = spec.url(env, base_path)
    if not no_confirm:
        result = proxygen_api.get_instance(api, env, instance)
        if not result:
            raise click.ClickException(f"No such instance {_url}")
        output.print_spec(result)
        if not click.confirm(f"Delete the instance at {_url}?"):
            raise click.Abort()
    
    with yaspin() as sp:
        sp.text = f"Deleting {_url}"
        api = ctx.obj["api"]
        instance = parse.quote(base_path)
        result = proxygen_api.delete_instance(api, env, instance)
        sp.ok("✔")
