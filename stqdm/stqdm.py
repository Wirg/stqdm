import re
from typing import Optional

import streamlit as st
from packaging import version
from tqdm.auto import tqdm

IS_TEXT_INSIDE_PROGRESS_AVAILABLE = version.parse(st.__version__) >= version.parse("1.18.0")
BAR_FORMAT_REGEX = re.compile(r"\{bar(?:[:!][a-zA-Z0-9]+){,2}}")


class stqdm(tqdm):  # pylint: disable=invalid-name,inconsistent-mro
    def __init__(
        self,
        iterable=None,
        desc=None,
        total=None,
        leave=True,
        file=None,
        ncols=None,
        mininterval=0.1,
        maxinterval=10.0,
        miniters=None,
        ascii=None,  # pylint: disable=redefined-builtin
        disable=False,
        unit="it",
        unit_scale=False,
        dynamic_ncols=False,
        smoothing=0.3,
        bar_format=None,
        initial=0,
        position=None,
        postfix=None,
        unit_divisor=1000,
        write_bytes=None,
        lock_args=None,
        nrows=None,
        colour=None,
        gui=False,
        st_container=None,
        backend=False,
        frontend=True,
        **kwargs,
    ):  # pylint: disable=too-many-arguments,too-many-locals
        if st_container is None:
            st_container = st
        self._backend = backend
        self._frontend = frontend
        self.st_container = st_container
        self._st_progress_bar = None
        self._st_text = None

        if ncols is None and not bar_format:
            ncols = 0  # rely on standard tqdm way to not display progress bar
        if bar_format:
            original_bar_format = bar_format
            bar_format = self.remove_bar_from_format(original_bar_format)
            should_display_progress_bar = bar_format != original_bar_format
            should_display_text = bool(bar_format.strip())
        else:
            should_display_progress_bar = True
            should_display_text = True
        self.should_display_progress_bar = should_display_progress_bar
        self.should_display_text = should_display_text

        super().__init__(
            iterable=iterable,
            desc=desc,
            total=total,
            leave=leave,
            file=file,
            ncols=ncols,
            mininterval=mininterval,
            maxinterval=maxinterval,
            miniters=miniters,
            ascii=ascii,
            disable=disable,
            unit=unit,
            unit_scale=unit_scale,
            dynamic_ncols=dynamic_ncols,
            smoothing=smoothing,
            bar_format=bar_format,
            initial=initial,
            position=position,
            postfix=postfix,
            unit_divisor=unit_divisor,
            write_bytes=write_bytes,
            lock_args=lock_args,
            nrows=nrows,
            colour=colour,
            gui=gui,
            **kwargs,
        )

    @property
    def st_progress_bar(self) -> st.progress:
        if self._st_progress_bar is None:
            self._st_progress_bar = self.st_container.empty()
        return self._st_progress_bar

    @property
    def st_text(self) -> st.empty:
        if self._st_text is None:
            self._st_text = self.st_container.empty()
        return self._st_text

    def st_display(self, n: int, total: Optional[int], **kwargs) -> None:  # pylint: disable=invalid-name
        if self.should_display_text:
            meter_text = self.format_meter(n, total, **kwargs)
        else:
            meter_text = None

        can_display_text = bool(meter_text)
        can_display_progress_bar = total is not None and total > 0

        if can_display_progress_bar and self.should_display_progress_bar:
            if not can_display_text:
                self.st_progress_bar.progress(n / total)
            elif IS_TEXT_INSIDE_PROGRESS_AVAILABLE:
                self.st_progress_bar.progress(n / total, text=meter_text)
            else:
                self._st_text.write(meter_text)
                self.st_progress_bar.progress(n / total)
        else:
            if can_display_text:
                self.st_text.write(meter_text)

    def display(self, msg=None, pos=None) -> bool:
        if self._backend:
            super().display(msg, pos)
        if self._frontend:
            self.st_display(**self.format_dict)
        return True

    def st_clear(self) -> None:
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
