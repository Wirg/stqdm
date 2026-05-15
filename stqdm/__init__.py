from importlib.metadata import PackageNotFoundError, version

from stqdm.stqdm import stqdm

try:
    __version__ = version("stqdm")
except PackageNotFoundError:
    __version__ = "0+unknown"
