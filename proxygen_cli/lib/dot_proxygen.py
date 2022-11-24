"""
Get or create proxygen config directory.

Should be at ~/.proxygen.
"""
import pathlib

def directory() ->pathlib.Path:
    """
    Return the proxygen config directory as a pathlib.Path object.
    Creates it if it does not exist.
    """
    _dir = pathlib.Path.home().joinpath(".proxygen")
    if not _dir.exists():
        _dir.mkdir()
    return _dir


def _get_create_file(filename) -> pathlib.Path:
    _file = directory().joinpath(filename)
    if not _file.exists():
        _file.touch()
    return _file


def settings_file() -> pathlib.Path:
    """
    Return the proxygen config file as a pathlib.Path object.
    Creates it if it does not exist.
    """
    return _get_create_file("settings.yaml")


def credentials_file() -> pathlib.Path:
    """
    Return the proxygen credentials file as a pathlib.Path object.
    Creates it if it does not exist.
    """
    return _get_create_file("credentials.yaml")


def token_cache_file() -> pathlib.Path:
    return _get_create_file("token_cache.json")
