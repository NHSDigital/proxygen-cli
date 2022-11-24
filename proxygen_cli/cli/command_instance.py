from typing import get_args
from urllib import parse

import click

from proxygen_cli.lib import output, proxygen_api, spec
from proxygen_cli.lib.settings import SETTINGS
from proxygen_cli.lib.constants import LITERAL_ENVS

CHOICE_OF_ENVS = click.Choice(get_args(LITERAL_ENVS))

def url(env, base_path):
    sub_domain = "api" if env == "prod" else f"{env}.api"
    return f"https://{sub_domain}.service.nhs.uk/{base_path}"    


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
        result = {
            "environments": {
                env: proxygen_api.get_api_environment(api, env)
            }
        }
    else:
        result = proxygen_api.get_api(api)

    # objects = []
    # for env in result["environments"]:
    #     instances = result["environments"][env]["instances"]
    #     secrets = result["environments"][env]["secrets"]

    #     for instance in instances:
    #         objects.append({"type": "instance", "name": instance, "environment": env})
    #     for secret in secrets:
    #         objects.append({"type": "secret", "name": instance, "environment": env})

    # cli_output.output(objects)
    output.print_json(result)


@instance.command()
@click.argument("env", type=CHOICE_OF_ENVS)
@click.argument("base_path")
@click.argument("spec_file")
@click.option(
    "--no-confirm", is_flag=True, show_default=True, help="Do not prompt for confirmation."
)
@click.pass_context
def describe(ctx, env, base_path, spec_file, no_confirm):
    """
    Deploy <SPEC_FILE> to https://<ENV>.api.service.nhs.uk/<BASE_PATH>

    If <ENV> is "prod" then deploy to https://api.service.nhs.uk/<BASE_PATH>
    """

    
    paas_open_api = spec.resolve(spec_file)

    # Overwrite the servers object to point to the values provided form the cli
    paas_open_api["servers"] = [{"url": url(env, base_path)}]

    if not no_confirm:
        output.print_spec(paas_open_api)
        if not click.confirm(f"Deploy this spec to {url}?"):
            raise click.Abort()

    api = ctx.obj["api"]
    instance = parse.quote(base_path)
    result = proxygen_api.put_instance(api, env, instance, paas_open_api)
    output.print_spec(result)

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

    if not no_confirm:
        result = proxygen_api.get_instance(api, env, instance)
        output.print_spec(result)
        if not click.confirm(f"Delete the api at {url(env, base_path)}?"):
            raise click.Abort()
    
    result = proxygen_api.delete_instance(api, env, instance)
    output.print_spec(result)
