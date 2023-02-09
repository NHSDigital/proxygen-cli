"""
A simple HTTP server for your spec.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from functools import partial
import json
import yaml

from .settings import SETTINGS
from .spec import resolve
from .output import to_spec

_RENDER_SPEC_METHOD = None


class SpecHttpRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", f"application/{SETTINGS.spec_output_format}")
        self.send_header("Access-Control-Allow-Origin", "*") # Enable CORS for swagger import
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        spec_str = to_spec(_RENDER_SPEC_METHOD())
        self.wfile.write(spec_str.encode())


def serve(*args, **kwargs):
    """
    Passes *args, **kwargs to spec.resolve
    """
    global _RENDER_SPEC_METHOD
    _RENDER_SPEC_METHOD = partial(resolve, *args, **kwargs)

    server_address = ("", 8008)
    httpd = HTTPServer(server_address, SpecHttpRequestHandler)
    httpd.serve_forever()
