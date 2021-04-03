"""init code of mk module."""
from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    pass
