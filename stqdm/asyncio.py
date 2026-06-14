from __future__ import annotations

# pylint: disable=invalid-name
from collections.abc import AsyncIterable, Iterable, Iterator
from typing import Any, Optional, cast

from typing_extensions import Unpack

from stqdm.stqdm import stqdm
from stqdm.types import STQDMArgs

__all__ = ["astqdm", "stqdm_asyncio", "tarange", "tqdm", "trange"]


class stqdm_asyncio(stqdm):
    """Async-aware STqdm entrypoint with dual-protocol iterable handling."""

    def __init__(
        self,
        iterable: Optional[Iterable[Any] | AsyncIterable[Any]] = None,
        **kwargs: Unpack[STQDMArgs],
    ) -> None:
        async_iterator = self._get_async_iterator(iterable)
        if async_iterator is None:
            sync_iterable = cast(Iterable[Any] | None, iterable)
            super().__init__(iterable=sync_iterable, **kwargs)
            self.iterable_awaitable = False
            if iterable is not None:
                if hasattr(iterable, "__next__"):
                    sync_iterator = cast(Iterator[Any], iterable)
                    self.iterable_iterator = sync_iterator
                    self.iterable_next = sync_iterator.__next__
                else:
                    self.iterable_iterator = iter(cast(Iterable[Any], iterable))
                    self.iterable_next = self.iterable_iterator.__next__
            return

        merged_kwargs = cast(STQDMArgs, dict(kwargs))
        if merged_kwargs.get("total") is None:
            inferred_total = self._safe_len(iterable)
            if inferred_total is not None:
                merged_kwargs["total"] = inferred_total
        super().__init__(iterable=None, **merged_kwargs)
        self.iterable_awaitable = True
        self.iterable_iterator = async_iterator
        self.iterable_next = async_iterator.__anext__

    @staticmethod
    def _get_async_iterator(iterable: Optional[Iterable[Any] | AsyncIterable[Any]]) -> Any | None:
        if iterable is None or hasattr(iterable, "__iter__"):
            return None
        if hasattr(iterable, "__anext__"):
            return iterable
        if hasattr(iterable, "__aiter__"):
            return aiter(cast(AsyncIterable[Any], iterable))
        return None

    @staticmethod
    def _safe_len(iterable: Optional[Iterable[Any] | AsyncIterable[Any]]) -> int | None:
        if iterable is None:
            return None
        try:
            return len(iterable)  # type: ignore[arg-type]
        except TypeError:
            return None


def tarange(*args: Any, **kwargs: Any) -> stqdm_asyncio:
    """Shortcut for `stqdm_asyncio(range(*args), **kwargs)`."""
    return stqdm_asyncio(range(*args), **kwargs)


tqdm = stqdm_asyncio
trange = tarange
astqdm = stqdm_asyncio
