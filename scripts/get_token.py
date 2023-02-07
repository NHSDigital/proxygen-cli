"""
Prints a token out to the terminal that can then be piped into other linux commands
Requires ~/.proxygen/token_cache.json to exist. To create this run any cli command that requires auth
    e.g. proxygen spec get
"""

import pathlib
import os
import json

def token():
    token_cache = pathlib.Path.home().joinpath(".proxygen").joinpath("token_cache.json")
    if not token_cache.exists():
        print("Token cache does not exist - check the settings and credential files and retry `proxygen spec get`")

    with token_cache.open("r", encoding="utf-8") as _file:
        contents = json.load(_file)
    
    token_key = next(iter(contents))
    token = contents[token_key]["id_token"]
    return token

if __name__ == "__main__":
    print(token())