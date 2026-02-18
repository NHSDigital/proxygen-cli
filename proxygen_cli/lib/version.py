from proxygen_cli.lib import proxygen_api
from proxygen_cli import __version__ as proxygen_cli_version

def validate_cli_version():
    status = proxygen_api.status()
    required = tuple(int(x) for x in status["proxygen_cli"]["min_version"].split("."))
    current = tuple(int(x) for x in proxygen_cli_version.split("."))
    if current < required:
        raise RuntimeError(f"This version proxygen-cli is out-of-date. Please update to {status['proxygen_cli']['min_version']}")
