from importlib.metadata import PackageNotFoundError, version

from stqdm.asyncio import astqdm, stqdm_asyncio
from stqdm.auto import tqdm, trange
from stqdm.stqdm import stqdm

__all__ = ["astqdm", "stqdm", "stqdm_asyncio", "tqdm", "trange"]

try:
    __version__ = version("stqdm")
except PackageNotFoundError:
    __version__ = "0+unknown"
