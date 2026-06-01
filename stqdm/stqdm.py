import io
import re
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Iterable, Iterator, Optional, cast

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
    """Custom tqdm progress bar integration for Streamlit applications, allowing for backend (server logs) and frontend (Streamlit) updates.

    Inherits from tqdm and modifies functionality to integrate progress bars into Streamlit interfaces.

    Attributes:
        st_container (DeltaGenerator): The Streamlit container for displaying progress bar.
        _backend (bool): Flag to enable or disable backend progress display. Backend is server log.
        _frontend (bool): Flag to enable or disable frontend progress display. Frontend is Streamlit interface.
    """

    def __init__(
        self,
        iterable: Optional[Iterable] = None,
        **kwargs: Unpack[STQDMArgs],
    ) -> None:  # pylint: disable=too-many-arguments,too-many-locals
        """Initializes stqdm with an iterable and optional arguments that define the behavior and display of the progress bar.

        Args:
            iterable (Optional[Iterable]): The iterable to wrap with the progress bar.
            **kwargs (Unpack[STQDMArgs]): Additional keyword arguments coming either from tqdm or from stqdm.
                stqdm arguments are st_container, backend, frontend.
        """
        kwargs = self.combine_default_and_provided_kwargs(provided_config=kwargs)

        self.st_container: "DeltaGenerator" = kwargs.pop("st_container", st.container())
        self._backend: bool = kwargs.pop("backend", False)
        self._frontend: bool = kwargs.pop("frontend", True)
        if not self._backend:
            # Route tqdm's terminal writes to an in-memory sink so close() cannot leak a trailing newline.
            kwargs["file"] = io.StringIO()

        # Will be set when necessary
        self._st_progress_bar: Optional["DeltaGenerator"] = None
        self._st_text: Optional["DeltaGenerator"] = None
        frontend_config = self.build_frontend_config_overrides(**kwargs)
        self._frontend_ncols: Optional[int] = frontend_config["ncols"]
        self._frontend_bar_format: Optional[str] = frontend_config["bar_format"]
        self.should_display_progress_bar: bool = frontend_config["should_display_progress_bar"]
        self.should_display_text: bool = frontend_config["should_display_text"]

        super().__init__(
            iterable=iterable,
            **kwargs,
        )

    ####
    # STQDM's default arguments handling with the scope manager
    ###
    scope_stack: ScopeManager[STQDMArgs] = ScopeManager(STQDMArgs())

    @classmethod
    def set_default_config(cls, /, **config: Unpack[STQDMArgs]) -> None:
        """Sets the default configuration for stqdm instances globally."""
        cls.scope_stack.set_default_config(config)

    @classmethod
    @contextmanager
    def scope(cls, /, **config: Unpack[STQDMArgs]) -> Iterator[STQDMArgs]:
        """A context manager to temporarily set a scoped configuration for stqdm instances."""
        with cls.scope_stack.scope(config) as scope:
            yield scope

    @classmethod
    def combine_default_and_provided_kwargs(cls, provided_config: STQDMArgs) -> STQDMArgs:
        """This function combine default of scope stack and provided kwargs.

        This is the logic that implements the default merge for configurations.
        The new config is the latest provided values in order:
        - default_config (less important)
        - active scopes, from outermost to innermost
        - current_config (stqdm call params) (most important)
        If you want to change this behavior, modify this function.

        Args:
            provided_config (STQDMArgs): A dictionary of configuration settings provided at the time of instance creation.

        Returns:
            STQDMArgs: A dictionary containing the merged configuration settings that will typically used at init.

        Examples:
            Config provided in the init of stqdm will be passed as provided_config.
            provided_config will override default one if there is a shared key (example with desc).
            >>> stqdm.set_default_config(frontend=False, desc="hello")
            ... stqdm.combine_default_and_provided_kwargs({"desc": "world"})
            {"frontend": False, "desc": "world"}

            Latest scope is used in the same way.
            >>> with stqdm.scope(frontend=False, desc="hello"):
            ...     stqdm.combine_default_and_provided_kwargs({"desc": "world"})
            {"frontend": False, "desc": "world"}

            Both default config and latest scope are used.
            >>> stqdm.set_default_config(frontend=True, backend=True, desc="hello")
            ... with stqdm.scope(frontend=False, desc="world"):
            ...     stqdm.combine_default_and_provided_kwargs({"desc": "again"})
            {"frontend": False, "backend": True, "desc": "again"}

            Nested scopes inherit values that they do not override.
            >>> with stqdm.scope(bar_format="{desc}", desc="outer"):
            ...     with stqdm.scope(desc="inner"):
            ...         stqdm.combine_default_and_provided_kwargs({})
            {"bar_format": "{desc}", "desc": "inner"}
        """
        return cls.scope_stack.use_current_default_if_config_not_provided(config=provided_config)

    ###
    # Internal Functions
    ###

    @property
    def st_progress_bar(self) -> "DeltaGenerator":
        """Lazily creates and returns a Streamlit container for the frontend progress bar."""
        if self._st_progress_bar is None:
            self._st_progress_bar = self.st_container.empty()
        return self._st_progress_bar

    @property
    def st_text(self) -> "DeltaGenerator":
        """Lazily creates and returns a Streamlit container for text associated with the frontend progress bar.

        This won't be used in latest version of streamlit. Since 1.18.0, text can be pushed with the progress bar.
        """
        if self._st_text is None:
            self._st_text = self.st_container.empty()
        return self._st_text

    def st_display(self, n: float, total: Optional[float], **kwargs) -> None:  # pylint: disable=invalid-name
        """Display the progress bar and text in streamlit (frontend).

        Progress bar is displayable if there is a total.
        Text is displayable if format allows it. IE: if the text is not empty. Typically bar_format={bar}.
        Since version 1.18.0 of streamlit, the text will be displayed together within the progress bar widget.
        Before, it required 2 components (a progress bar, and a text above).
        """
        if self.should_display_text:
            # cast to float because of issue with tqdm stubs typing
            meter_text = self.format_meter(n, cast(float, total), **kwargs)
        else:
            meter_text = None

        can_display_text = bool(meter_text)
        can_display_progress_bar = total is not None and total > 0

        if can_display_progress_bar and self.should_display_progress_bar:
            total = cast(float, total)  # total is not None
            progress = min(max(n / total, 0.0), 1.0)
            if not can_display_text:
                self.st_progress_bar.progress(progress)
            elif IS_TEXT_INSIDE_PROGRESS_AVAILABLE:
                self.st_progress_bar.progress(progress, text=meter_text)
            else:
                self.st_text.write(meter_text)
                self.st_progress_bar.progress(progress)
        else:
            if can_display_text:
                self.st_text.write(meter_text)

    def display(self, msg=None, pos=None) -> bool:  # type: ignore[override]
        """Overrides the tqdm display method to include frontend and backend logic.

        Frontend refers to streamlit web interface.
        Backend refers to streamlit server logs.
        """
        # TODO: for a weird reason, display is type -> None in the stubs but it is not in the code
        # TODO: check if we should return True or something related to what happened in backend
        if self._backend:
            super().display(msg, pos)
        if self._frontend:
            self.st_display(**self.frontend_format_dict)
        return True

    def st_clear(self) -> None:
        """Clear the streamlit frontend part if necessary. This is used in .close()."""
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
        """Close the progress bar."""
        if self.disable:
            # TQDM internal to avoid multiple closing
            return
        super().close()
        self.st_clear()

    @property
    def frontend_format_dict(self) -> dict[str, Any]:
        return {**self.format_dict, "ncols": self._frontend_ncols, "bar_format": self._frontend_bar_format}

    @staticmethod
    def build_frontend_config_overrides(**kwargs) -> dict[str, Any]:
        """This is an util for compatibility between bar_format in tqdm and stqdm.

        In tqdm's bar_format, {bar} is used to say where the bar will be.
        The default is typically: {l_bar}{bar}{r_bar}.
        In stqdm, there is not things like {l_bar} and {r_bar}.
        Text is either displayed above in another widget or on the right of the progress_bar widget when available.
        For this reason, we analyze the bar_format to understand if there is a {bar:something} inside and remove it.
        If we find a progress bar inside, new_bar_format != bar_format, then we will display the progress bar if possible.
        If after removing the progress bar, the bar_format is empty, then there is no text to display and we don't.

        Args:
            **kwargs: Arbitrary keyword arguments.
                Expected to contain:
                    ncols (int, optional): The number of columns for the progress bar.
                        If unspecified, progress bars  are not displayed by default.
                    bar_format (str, optional): The formatting string for the progress bar, which may include placeholders
                        like {bar}. This is modified to fit stqdm's display capabilities.

        Returns:
            dict[str, Any]: A dictionary containing updated configurations for the frontend display, including:
                - ncols: Adjusted number of columns for the progress bar.
                - bar_format: Modified bar format string, stripped of unsupported placeholders.
                - should_display_progress_bar (bool): Indicates whether the progress bar should be displayed.
                - should_display_text (bool): Indicates whether text should be displayed alongside or instead of the bar.
        """
        bar_format: Optional[str] = kwargs.get("bar_format")
        ncols: Optional[int] = kwargs.get("ncols")
        if bar_format is None:
            if ncols is None:
                ncols = 0
            should_display_progress_bar = True
            should_display_text = True
        elif bar_format == "":
            should_display_progress_bar = True
            should_display_text = False
        else:
            original_bar_format = bar_format
            # {bar:size} defines the bar + its size (default 10)
            bar_format = re.sub(BAR_FORMAT_REGEX, "", bar_format)
            should_display_progress_bar = bar_format != original_bar_format
            should_display_text = bool(bar_format.strip())
        return {
            # ncols should not impact text of stqdm's frontend
            # ncols = 0, forces a specific bar format
            "ncols": ncols,
            "bar_format": bar_format,
            "should_display_progress_bar": should_display_progress_bar,
            "should_display_text": should_display_text,
        }

    @staticmethod
    def remove_bar_from_format(bar_format: str) -> str:
        """Remove tqdm's terminal bar placeholder from text shown in Streamlit."""
        return re.sub(BAR_FORMAT_REGEX, "", bar_format)
