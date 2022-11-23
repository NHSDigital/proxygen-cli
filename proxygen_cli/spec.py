"""
Proxygen resolves internal file refs and remote refs.
We only need to resolve external file refs.
"""
from typing import List, Any, Union
import pathlib
from urllib.parse import urlparse

import yaml


def _find_file_refs(obj, obj_loc: List[Union[str, int]]=None):
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
        internal_ref = len(obj) > 0 and obj[0] == '#'
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
    

def resolve(file_name):
    root_file = pathlib.Path(file_name)
    if not root_file.exists() or root_file.is_dir():
        raise ValueError(f"No such file {root_file}")

    with root_file.open() as f:
        spec = yaml.safe_load(f)
    
    file_refs = _find_file_refs(spec)
    spec_dir = root_file.parent
    for keys, file_ref in file_refs:
        file_path = spec_dir.joinpath(file_ref)
        if not file_path.exists() or file_path.is_dir():
            raise ValueError(f"Unable to resolve $ref {file_path} at {keys}")
        with file_path.open() as f:
            sub_spec = yaml.safe_load(f)

        spec = _update_obj(spec, keys, sub_spec)
    return spec
