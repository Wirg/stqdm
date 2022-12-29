import streamlit as st
from tqdm.auto import tqdm


class stqdm(tqdm):  # pylint: disable=invalid-name
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

    def st_display(self, n, total, **kwargs):  # pylint: disable=invalid-name
        if total is not None and total > 0:
            self.st_text.write(self.format_meter(n, total, **{**kwargs, "ncols": 0}))
            self.st_progress_bar.progress(n / total)
        if total is None:
            self.st_text.write(self.format_meter(n, total, **{**kwargs, "ncols": 0}))

    def display(self, msg=None, pos=None):
        if self._backend:
            super().display(msg, pos)
        if self._frontend:
            self.st_display(**self.format_dict)
        return True

    def st_clear(self):
        if self._st_text is not None:
            self._st_text.empty()
            self._st_text = None
        if self._st_progress_bar is not None:
            self._st_progress_bar.empty()
            self._st_progress_bar = None

    def close(self):
        super().close()
        self.st_clear()
