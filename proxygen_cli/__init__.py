"""Pypi packaging init"""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore[no-redef]

__version__ = importlib_metadata.version(__name__)
_package_name = importlib_metadata.metadata(__name__)["Name"]
