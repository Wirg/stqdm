import re
from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterable, Iterator, Optional, cast

import streamlit as st
from packaging import version
from tqdm.auto import tqdm
from typing_extensions import Unpack

from stqdm.configuration_manager import ScopeManager
from stqdm.types import STQDMArgs

# pragma: no cover
if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator

IS_TEXT_INSIDE_PROGRESS_AVAILABLE = version.parse(st.__version__) >= version.parse("1.18.0")
BAR_FORMAT_REGEX = re.compile(r"\{bar(?:[:!][a-zA-Z0-9]+){,2}}")


class stqdm(tqdm):  # pylint: disable=invalid-name,inconsistent-mro
    def __init__(
        self,
        iterable: Optional[Iterable] = None,
        **kwargs: Unpack[STQDMArgs],
    ) -> None:  # pylint: disable=too-many-arguments,too-many-locals
        kwargs = self.combine_default_and_provided_kwargs(provided_config=kwargs)

        self.st_container: "DeltaGenerator" = kwargs.pop("st_container", st.container())
        self._backend: bool = kwargs.pop("backend", False)
        self._frontend: bool = kwargs.pop("frontend", True)

        # Will be set when necessary
        self._st_progress_bar: Optional["DeltaGenerator"] = None
        self._st_text: Optional["DeltaGenerator"] = None

        # Handle the way we will display the progress bar
        # TODO: /!\ we are modifying both argument for backend and frontend
        ncols: Optional[int] = kwargs.get("ncols")
        bar_format: Optional[str] = kwargs.get("bar_format")
        if ncols is None and bar_format is None:
            ncols = 0  # rely on standard tqdm way to not display progress bar
        if bar_format:
            original_bar_format = bar_format
            bar_format = self.remove_bar_from_format(original_bar_format)
            should_display_progress_bar = bar_format != original_bar_format
            should_display_text = bool(bar_format.strip())
        else:
            should_display_progress_bar = True
            should_display_text = True
        self.should_display_progress_bar: bool = should_display_progress_bar
        self.should_display_text: bool = should_display_text

        kwargs["ncols"] = ncols
        kwargs["bar_format"] = bar_format

        super().__init__(
            iterable=iterable,
            **kwargs,
        )

    scope_stack: ScopeManager[STQDMArgs] = ScopeManager(STQDMArgs())

    @classmethod
    def set_default_config(cls, /, **config: Unpack[STQDMArgs]) -> None:
        cls.scope_stack.default_config = config

    @classmethod
    @contextmanager
    def scope(cls, /, **config: Unpack[STQDMArgs]) -> Iterator[STQDMArgs]:
        with cls.scope_stack.scope(config) as scope:
            yield scope

    @classmethod
    def combine_default_and_provided_kwargs(cls, provided_config: STQDMArgs) -> STQDMArgs:
        """This function combine default of scope stack and provided kwargs.

        By default, we use kwargs from the current scope unless they are provided.
        If you want to change this behavior, modify this function.
        """
        return cls.scope_stack.use_current_default_if_config_not_provided(config=provided_config)

    # Internal Functions
    @property
    def st_progress_bar(self) -> "DeltaGenerator":
        if self._st_progress_bar is None:
            self._st_progress_bar = self.st_container.empty()
        return self._st_progress_bar

    @property
    def st_text(self) -> "DeltaGenerator":
        if self._st_text is None:
            self._st_text = self.st_container.empty()
        return self._st_text

    def st_display(self, n: float, total: Optional[float], **kwargs) -> None:  # pylint: disable=invalid-name
        """Display the progress bar and text in streamlit"""
        if self.should_display_text:
            # cast to float because of issue with tqdm stubs typing
            meter_text = self.format_meter(n, cast(float, total), **kwargs)
        else:
            meter_text = None

        can_display_text = bool(meter_text)
        can_display_progress_bar = total is not None and total > 0

        if can_display_progress_bar and self.should_display_progress_bar:
            total = cast(float, total)  # total is not None
            if not can_display_text:
                self.st_progress_bar.progress(n / total)
            elif IS_TEXT_INSIDE_PROGRESS_AVAILABLE:
                self.st_progress_bar.progress(n / total, text=meter_text)
            else:
                self.st_text.write(meter_text)
                self.st_progress_bar.progress(n / total)
        else:
            if can_display_text:
                self.st_text.write(meter_text)

    def display(self, msg=None, pos=None) -> bool:  # type: ignore[override]
        # TODO: for a weird reason, display is type -> None in the stubs but it is not in the code
        # TODO: check if we should return True or something related to what happend in backend
        if self._backend:
            super().display(msg, pos)
        if self._frontend:
            self.st_display(**self.format_dict)
        return True

    def st_clear(self) -> None:
        leave = self.pos == 0 if self.leave is None else self.leave
        if leave:
            return
        if self._st_text is not None:
            self._st_text.empty()
            self._st_text = None
        if self._st_progress_bar is not None:
            self._st_progress_bar.empty()
            self._st_progress_bar = None

    def close(self) -> None:
        super().close()
        self.st_clear()

    @staticmethod
    def remove_bar_from_format(bar_format: str) -> str:
        return re.sub(BAR_FORMAT_REGEX, "", bar_format)
