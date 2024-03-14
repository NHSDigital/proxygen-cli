from typing import get_args

import click
from yaspin import yaspin

from proxygen_cli.lib import output, proxygen_api, version
from proxygen_cli.lib.settings import SETTINGS
from proxygen_cli.lib.constants import LITERAL_ENVS, LITERAL_SECRET_TYPES
from typing import Optional

CHOICE_OF_ENVS = click.Choice(get_args(LITERAL_ENVS))
CHOICE_OF_SECRET_TYPES = click.Choice(get_args(LITERAL_SECRET_TYPES))


@click.group()
@click.option(
    "--api", default=SETTINGS.api, help="Override the default API", show_default=True
)
@click.pass_context
def secret(ctx, api):
    """
    Create/Update/Delete secrets used by your API.
    """
    version.validate_cli_version()
    ctx.ensure_object(dict)
    ctx.obj["api"] = api
    if api is None:
        raise click.UsageError(
            "You must set the API before using this command: see `proxygen settings`"
        )


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
        result = proxygen_api.get_secrets(api, env)
    else:
        result = proxygen_api.get_resources(api, _type="secret")
    output.print_table(result)


def _validate_put_options(
    secret_value: str, secret_file: str, apikey: bool, mtls_cert: str, mtls_key: str
) -> Optional[str]:
    """
    Ensure that the provided command line options make sense for the perceived
    context.

    Returns the secret type as a string, or None
    """

    secret_type = None

    if any([mtls_cert, mtls_key]):
        if not all([mtls_cert, mtls_key]):
            raise click.UsageError("Please specify both --mtls-cert and --mtls-key.")
        secret_type = "mtls"

    if (secret_type == "mtls" and (secret_value or secret_file)) or (
        secret_type != "mtls" and not any([secret_value, secret_file])
    ):
        raise click.UsageError(
            "Please specify either of --secret-value and --secret-file, "
            "or --mtls-cert with --mtls-key."
        )

    if secret_value is not None and secret_file is not None:
        raise click.UsageError(
            "Please specify one of --secret-value" " and --secret-file, not both."
        )

    if apikey:
        secret_type = "apikey"
    elif mtls_cert:
        # both will be populated at this point
        secret_type = "mtls"

    return secret_type


def _read_or_fail(secret_file: str, type_label: str) -> str:
    """
    Read the contents of the secret file.

    Raises a ValueError if the file cannot be read.

    :param secret_file: The path to the secret file.
    :param type_label: A label describing the type of secret.
    :return: The contents of the secret file.
    """
    try:
        with open(secret_file, encoding="utf-8") as file_desc:
            return file_desc.read()
    except FileNotFoundError as ex:
        raise ValueError(
            f"Missing or undreadable {type_label} " f"file {secret_file}."
        ) from ex


@secret.command()
@click.argument("env", type=CHOICE_OF_ENVS)
@click.argument("secret_name")
@click.option("--secret-value")
@click.option("--secret-file")
@click.option("--apikey", is_flag=True, help="Tag this secret as an apikey")
@click.option(
    "--mtls-cert", help="Provide a path to a PEM encoded certificate for mutual TLS"
)
@click.option(
    "--mtls-key", help="Provide a path to a PEM encoded private key for mutual TLS"
)
@click.pass_context
def put(ctx, env, secret_name, secret_value, secret_file, apikey, mtls_cert, mtls_key):
    """
    Create or overwrite a secret.

    This command makes the secret available to your instances.
    """

    api = ctx.obj["api"]

    inferred_secret_type = _validate_put_options(
        secret_value, secret_file, apikey, mtls_cert, mtls_key
    )

    with yaspin() as spinner:
        spinner.text = f"Putting secret {secret_name} in {env}"

        try:
            if inferred_secret_type == "mtls":
                mtls_cert = _read_or_fail(mtls_cert, "mTLS certificate")
                mtls_key = _read_or_fail(mtls_key, "mTLS private key")
                result = proxygen_api.put_mtls_secret(
                    api, env, secret_name, mtls_cert, mtls_key
                )
            else:
                secret_contents = secret_value or _read_or_fail(secret_file, "secret")
                result = proxygen_api.put_secret(
                    api, env, secret_name, inferred_secret_type, secret_contents
                )

            spinner.ok("✔")
        except Exception as ex:
            spinner.fail("✘")
            raise click.ClickException(
                f"Failed to put secret {secret_name} in {env}: {ex}"
            )

    output.print_json(result)


@secret.command()
@click.argument("env", type=CHOICE_OF_ENVS)
@click.argument("secret_type", type=CHOICE_OF_SECRET_TYPES)
@click.argument("secret_name")
@click.pass_context
def describe(ctx, env, secret_type, secret_name):
    """
    Describe a secret.
    """
    api = ctx.obj["api"]
    result = proxygen_api.get_secret(api, env, secret_type, secret_name)
    output.print_json(result)


@secret.command()
@click.argument("env", type=CHOICE_OF_ENVS)
@click.argument("secret_type", type=CHOICE_OF_SECRET_TYPES)
@click.argument("secret_name")
@click.option(
    "--no-confirm",
    is_flag=True,
    show_default=True,
    help="Do not prompt for confirmation.",
)
@click.pass_context
def delete(ctx, env, secret_type, secret_name, no_confirm):
    """
    Delete a secret.
    """
    api = ctx.obj["api"]

    if not no_confirm:
        result = proxygen_api.get_secret(api, env, secret_type, secret_name)
        if result is None:
            raise click.BadArgumentUsage(
                f"A secret named {secret_name} does not exist in {env}."
            )
        output.print_json(result)
        if not click.confirm(f"Delete secret {secret_name} from {env}?"):
            raise click.Abort()
    with yaspin() as sp:
        sp.text = f"Deleting secret {secret_name} from {env}"
        try:
            result = proxygen_api.delete_secret(api, env, secret_type, secret_name)
            if result is None:
                raise click.ClickException(f"No such secret {secret_name} in {env}")
            sp.ok("✔")
        except Exception as e:
            sp.fail("✘")
            raise click.ClickException(
                f"Failed to delete secret {secret_name} from {env}: {e}"
            )
