try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError: # pragma: no cover
    import importlib_metadata

__version__ = importlib_metadata.version(__name__)
_package_name = importlib_metadata.metadata(__name__)["Name"]
