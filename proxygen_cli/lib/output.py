from typing import List, Dict
import json
import yaml
from datetime import datetime

import click
from tabulate import tabulate

from proxygen_cli.lib.settings import SETTINGS

def _format_time(obj: Dict[str, str], keys: List[str] = None):

    if keys is None:
        return obj

    for key in keys:
        _date_time = obj.pop("last_modified")
        d = datetime.fromisoformat(_date_time)
        s = d.strftime("%Y-%m-%d %H:%M")
        obj[key] = s
    return obj


def yaml_multiline_string_pipe(dumper, data):
    text_list = [line.rstrip() for line in data.splitlines()]
    fixed_data = "\n".join(text_list)
    if len(text_list) > 1:
        return dumper.represent_scalar('tag:yaml.org,2002:str', fixed_data, style="|")
    return dumper.represent_scalar('tag:yaml.org,2002:str', fixed_data)

yaml.add_representer(str, yaml_multiline_string_pipe)

def print_spec(spec):
    if SETTINGS.spec_output_format == "yaml":
        return print_yaml(spec)
    elif SETTINGS.spec_output_format == "json":
        return print_json(spec)

def print_json(obj):
    return click.echo(json.dumps(obj, indent=2))    

def print_yaml(obj):
    return click.echo(yaml.dump(obj))

def print_table(objs: List[Dict[str, str]]):
    objs = [_format_time(obj, keys=["last_modified"]) for obj in sorted(objs, key=lambda x: x["last_modified"])]

    table_string = tabulate(objs,headers="keys")
    click.echo(table_string)
