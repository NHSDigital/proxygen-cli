"""
Proxygen resolves internal file refs and remote refs.
We only need to resolve external file refs.
"""
import os
from typing import Dict, List, Union
import pathlib
from urllib.parse import urlparse

import yaml
import click
import jinja2


def _find_file_refs(obj, obj_loc: List[Union[str, int]] = None):
    if obj_loc is None:
        obj_loc = []

    if isinstance(obj, dict):
        refs = []
        for key, value in obj.items():
            refs = refs + _find_file_refs(value, obj_loc + [key])
        return refs
    elif isinstance(obj, list):
        refs = []
        for index, item in enumerate(obj):
            refs = refs + _find_file_refs(item, obj_loc + [index])
        return refs
    elif isinstance(obj, str) and obj_loc and obj_loc[-1] == "$ref":
        internal_ref = len(obj) > 0 and obj[0] == "#"
        url_parsed = urlparse(obj)
        remote_ref = True if url_parsed.scheme else False
        if not remote_ref and not internal_ref:
            # Then it's a file ref, which is what we're looking for!
            return [(obj_loc, obj)]
        return []
    return []


def _update_obj(obj, keys, sub_obj):

    if len(keys) > 1:
        obj[keys[0]] = _update_obj(obj[keys[0]], keys[1:], sub_obj)
        return obj
    elif len(keys) == 1:
        return sub_obj
    else:
        raise ValueError("Cannot update obj with no keys.")


def resolve(file_name, api, env, base_path):
    root_file = pathlib.Path(file_name)
    if not root_file.exists() or root_file.is_dir():
        raise click.ClickException(f"No such file {root_file}")

    jinja_env = jinja2.Environment(
        undefined=jinja2.StrictUndefined,
        variable_start_string="${",  # Use var syntax as ${ VARIABLE } so that param spec file is valid YAML.
        variable_end_string="}",
    )
    default_config_vars = get_default_config_vars(api, env, base_path)
    # Jinja vars set as implied (from CLI params) vars and environment vars
    jinja_vars = {**default_config_vars, **os.environ}

    def load_templated_yaml(template: str) -> Dict:
        try:
            # Sub jinja variables
            yml_str = jinja_env.from_string(template).render(jinja_vars)
        except jinja2.UndefinedError as exc:
            raise click.ClickException(
                f"{exc}\nHint: All jinja variables must be defined in an environment variable or one of {', '.join(default_config_vars.keys())}"
            )

        try:
            return yaml.safe_load(yml_str)

        except yaml.YAMLError as exc:
            raise click.ClickException(
                f"{exc}\nHint: Spec file is most likely not valid YAML"
            )

    with root_file.open() as f:
        spec = load_templated_yaml(f.read())

    file_refs = _find_file_refs(spec)
    spec_dir = root_file.parent.absolute().resolve()
    for keys, file_ref in file_refs:
        file_path = spec_dir.joinpath(file_ref)
        if not file_path.exists() or file_path.is_dir():
            raise click.ClickException(f"Unable to resolve $ref {file_path} at {keys}")
        with file_path.open() as f:
            sub_spec = load_templated_yaml(f.read())

        spec = _update_obj(spec, keys, sub_spec)
    return spec


def host(env):
    sub_domain = "api" if env == "prod" else f"{env}.api"
    return f"https://{sub_domain}.service.nhs.uk"


def url(env, base_path):
    return f"{host(env)}/{base_path}"


def get_default_config_vars(api, env, base_path):
    return {
        "BASE_PATH": base_path,
        "API": api,
        "ENVIRONMENT": env,
        "HOST": host(env),
        "BASE_URL": url(env, base_path),
    }
