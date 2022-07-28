
from typing_extensions import Required
from unittest import case
import click
import json
import yaml
import os
from pathlib import Path


from state import AuthConfig, UserAuth, get_cached_client, update_config, MachineAuth

DEFAULT_INSTANCE_JSON = "instance.json"
DEFAULT_INSTANCE_YAML = "instance.yml"
DEFAULT_INSTANCE_FILE = Path.cwd() / "instance.json"
PAAS_URL = "https://proxygen.ptl.api.platform.nhs.uk"

def _delete_instance_url(api_name, instance, apply=False):
  return f"{PAAS_URL}/apis/{api_name}/instances/{instance['name']}?{apply=}"

def _post_instance_url(api_name, apply=False):
  return f"{PAAS_URL}/apis/{api_name}/instances?{apply=}"

def _api_info_url(api_name):
  return f"{PAAS_URL}/apis/{api_name}"

def _docker_login(api_name):
  return f"{PAAS_URL}/apis/{api_name}/docker-token"

def _get_loader(instance_path):
  if instance_path.suffix == ".json":
    return json.load
  elif instance_path.suffix == ".yml":
    return yaml.load
  else:
      raise click.BadArgumentUsage(f"Instance file {DEFAULT_INSTANCE_JSON} must be in cwd or specified via --instance param")

def _load_instance(instance_name: str):
  loader = _get_loader(instance_name)
  with open(instance_name, "r") as f:
    try:
      return loader(f)
    except json.JSONDecodeError:
      raise click.BadArgumentUsage(f"Instance file {instance_name} must be valid JSON")

@click.group()
@click.option('--api-name', help="Specify via --api-name or env var PAAS_API_NAME", required=True)
@click.option('--instance', type=click.Path(exists=True), help="PaaS API config. Defaults to instance.json in cwd", default=DEFAULT_INSTANCE_FILE)
@click.pass_context
def cli(ctx, instance, api_name):
  ctx.ensure_object(dict)
  if ctx.invoked_subcommand in ("setup-machine-user", "setup-user"):
    return
  ctx.obj['INSTANCE_FILE'] = instance
  ctx.obj['INSTANCE'] = _load_instance(instance)
  ctx.obj['API_NAME'] = api_name
  ctx.obj['CLIENT'] = get_cached_client()


@cli.command
@click.pass_context
def check(ctx):
  paas_client = ctx.obj["CLIENT"]
  api_name = ctx.obj["API_NAME"]
  instance = ctx.obj["INSTANCE"]
  instance_file = ctx.obj["INSTANCE_FILE"]

  resp = paas_client.get(_api_info_url(api_name))
  connection = "Connected" if resp.status_code == 200 else "Not connected"
  click.echo(f"PaaS Connection: {connection}\nAPI name: {api_name}\nInstance name: {instance['name']}\nInstance file: {instance_file}")

def _format_steps(steps):
  return "\n".join(steps)

def _format_json(_json):
  return json.dumps(_json, indent=4)

@cli.command
@click.pass_context
def plan(ctx):
  paas_client = ctx.obj["CLIENT"]
  api_name = ctx.obj["API_NAME"]
  instance = ctx.obj["INSTANCE"]
  instance_file = ctx.obj["INSTANCE_FILE"]

  resp = paas_client.post(_post_instance_url(api_name, apply=False), json=instance)
  if resp.status_code != 200:
    raise click.ClickException(f"HTTP error {resp.status_code}:\n{_format_json(resp.json())}")
  if resp.json()['status'] == "plan successfully complete":
    click.echo(f"Plan complete with steps to apply:\n{_format_steps(resp.json()['steps not applied'])}")
  else:
    click.echo(f"Plan failed with message: {resp.json()['status']}")


@cli.command
@click.pass_context
def apply(ctx):
  paas_client = ctx.obj["CLIENT"]
  api_name = ctx.obj["API_NAME"]
  instance = ctx.obj["INSTANCE"]
  instance_file = ctx.obj["INSTANCE_FILE"]

  resp = paas_client.post(_post_instance_url(api_name, apply=True), json=instance)
  if resp.status_code != 200:
    raise click.ClickException(f"HTTP error {resp.status_code}:\n{_format_json(resp.json())}")
  elif resp.json()['status'] == "execution successfully complete":
    click.echo(f"Apply complete!")
  else:
    click.echo(f"Apply failed with message: {resp.json()['status']} with error {resp.json()['error']}")

@cli.command
@click.pass_context
@click.option('--apply', is_flag=True, show_default=True, default=False, help="Apply the destroy changes")
def destroy(ctx, apply):
  paas_client = ctx.obj["CLIENT"]
  api_name = ctx.obj["API_NAME"]
  instance = ctx.obj["INSTANCE"]
  instance_file = ctx.obj["INSTANCE_FILE"]

  if apply:
    click.echo(f"!!!! Warning you are about to delete {instance['name']} of API {api_name} !!!!")
    click.echo("This can take up to 20 minutes to fully complete...")
    user_input = click.prompt(f"Enter the text '{api_name}' to continue", type=str)
    if user_input != api_name:
      click.echo("Cancelling...")
      return

  resp = paas_client.delete(_delete_instance_url(api_name, instance, apply=apply), timeout=60*20)
  if resp.status_code != 200:
    raise click.ClickException(f"HTTP error {resp.status_code}:\n{_format_json(resp.json())}")
  else:
    click.echo(f"Destroy complete on {api_name} with message: {resp.json()['status']}")

  if not apply:
      click.echo("To apply changes supply the flag '--apply'")

@cli.command
@click.pass_context
def docker_login(ctx):
  paas_client = ctx.obj["CLIENT"]
  api_name = ctx.obj["API_NAME"]
  resp = paas_client.get(_docker_login(api_name))
  if resp.status_code != 200:
    raise click.ClickException(f"HTTP error {resp.status_code}:\n{_format_json(resp.json())}")

  click.echo(f"echo docker login -u {resp.json()['user']} --password {resp.json()["password"]} {resp.json()['registry']}")

@cli.command()
@click.option('--client-id', type=str, prompt=True)
@click.option('--base-url', type=str, default='https://identity.ptl.api.platform.nhs.uk')
@click.option('--private-key', type=click.Path(exists=True), prompt=True)
def setup_machine_user(client_id, base_url, private_key):
  config = MachineAuth(client_id=client_id, base_url=base_url, private_key=private_key)
  update_config(config)

@cli.command()
@click.option('--client-id', type=str, prompt=True)
@click.option('--client-secret', type=str, prompt=True)
@click.option('--user', type=str, prompt=True)
@click.option('--base-url', type=str, default='https://identity.ptl.api.platform.nhs.uk')
def setup_user(client_id, client_secret, user, base_url):
  config = UserAuth(client_id=client_id, client_secret=client_secret, base_url=base_url, username=user)
  update_config(config)

def main():
  cli(auto_envvar_prefix="PAAS")

