from pkg_resources import parse_version

from proxygen_cli.lib import proxygen_api
from proxygen_cli import __version__ as proxygen_cli_version


def validate_cli_version():
    status = proxygen_api.status()
    required_cli_version = parse_version(status["proxygen_cli"]["min_version"])
    current_cli_version = parse_version(proxygen_cli_version)
    if current_cli_version < required_cli_version:
        raise RuntimeError(f"This version proxygen-cli is out-of-date. Please update to {required_cli_version}")
    
