"""
Use python requests to manually hit a proxygen endpoint
Takes the full url and method as a command line argument

Usage: 
    python scripts/manual_endpoint.py GET http://localhost:9005/apis/hello-paas
"""

import sys
import requests
from scripts.get_token import token
import os
from pprint import pprint

FUNCTIONS = {
    "GET": requests.get,
    "POST": requests.post,
    "PUT": requests.put,
    "DELETE": requests.delete
}

def manual_curl(method, url):
    try:
        func = FUNCTIONS[method]
    except KeyError:
        return print("Invalid method")

    headers = {"Authorization": f"Bearer {token()}"}

    res = func(url, headers=headers)

    try: 
        content = res.json()
    except ValueError:
        content = res.text

    return res.status_code, content
    

if __name__ == "__main__":
    METHOD = sys.argv[1]
    URL = sys.argv[2]
    
    status_code, content = manual_curl(METHOD, URL)

    # Token may have expired
    if status_code in [401, 403]:
        os.system("proxygen spec get")
    
    status_code, content = manual_curl(METHOD, URL)

    pprint(content)
    print(f"Status code = {status_code}")
    