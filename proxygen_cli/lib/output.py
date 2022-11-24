import json
import yaml

import click


def yaml_multiline_string_pipe(dumper, data):
    text_list = [line.rstrip() for line in data.splitlines()]
    fixed_data = "\n".join(text_list)
    if len(text_list) > 1:
        return dumper.represent_scalar('tag:yaml.org,2002:str', fixed_data, style="|")
    return dumper.represent_scalar('tag:yaml.org,2002:str', fixed_data)

yaml.add_representer(str, yaml_multiline_string_pipe)

def print_json(obj):
    return click.echo(json.dumps(obj, indent=2))    

def print_yaml(obj):
    return click.echo(yaml.dump(obj))
