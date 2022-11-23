"""
Factory methods for consistent click options
"""
from typing import get_args

from click import Option

from proxygen_cli import constants


API = 
def api(): # Always required
    return API

def environment(prompt: bool=False):
    return 

def instance(prompt: bool=True):
    return 

def secret(required: bool=True):
    return Option("--secret", prompt=prompt)
