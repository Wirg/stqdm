from __future__ import annotations

# ruff: noqa: I001
# pylint: disable=import-outside-toplevel

import time


def long_running_task(seconds: float) -> None:
    """Simulate a long running task."""
    time.sleep(seconds)


def simple_stqdm_in_main(stop_iterations: int = 10, total_iterations: int = 50, task_duration: float = 0.01) -> None:
    """Simple example using stqdm with a standard for loop in the main area."""
    from stqdm import stqdm

    from demo.src import demo_apps

    for _ in stqdm(range(0, stop_iterations), total=total_iterations):
        demo_apps.long_running_task(task_duration)


def stqdm_in_sidebar(iterations: int = 10, task_duration: float = 0.01) -> None:
    """Render a progress bar in the Streamlit sidebar."""
    import streamlit as st
    from stqdm import stqdm

    from demo.src import demo_apps

    for _ in stqdm(range(iterations), st_container=st.sidebar):
        demo_apps.long_running_task(task_duration)


def stqdm_in_columns(iterations: int = 10, task_duration: float = 0.01) -> None:
    """Render progress bars in several Streamlit columns."""
    import streamlit as st
    from stqdm import stqdm

    from demo.src import demo_apps

    columns = st.columns(3)
    for column_index in (1, 2, 0):
        with columns[column_index]:
            for _ in stqdm(range(iterations)):
                demo_apps.long_running_task(task_duration)


def stqdm_multi_bars_in_columns(iterations: int = 10, task_duration: float = 0.01) -> None:
    """Render multiple progress bars in columns, stopping each bar at a different point."""
    import streamlit as st
    from stqdm import stqdm

    from demo.src import demo_apps

    columns = st.columns(3)
    stop_points = (3, 5, 7)
    for column_index, stop_point in zip((1, 2, 0), stop_points):
        with columns[column_index]:
            for index in stqdm(range(iterations)):
                demo_apps.long_running_task(task_duration)
                if index == stop_point:
                    break


def stqdm_in_main_nested(outer_iterations: int = 3, inner_iterations: int = 4, task_duration: float = 0.01) -> None:
    """Render nested progress bars and clear each inner bar after it finishes."""
    from stqdm import stqdm

    from demo.src import demo_apps

    for _ in stqdm(range(outer_iterations)):
        progress_bar = stqdm(range(inner_iterations))
        for _ in progress_bar:
            demo_apps.long_running_task(task_duration)
        progress_bar.st_clear()


def stqdm_no_total_no_length(iterations: int = 10, task_duration: float = 0.01) -> None:
    """Use stqdm with a generator that has no length and no explicit total."""
    import streamlit as st
    from stqdm import stqdm

    from demo.src import demo_apps

    for index in stqdm(index for index in range(iterations)):
        st.write(index)
        demo_apps.long_running_task(task_duration)


def stqdm_with_generator(values: tuple[str, ...] = ("a", "b", "c"), task_duration: float = 0.01) -> None:
    """Use stqdm with a simple generator-like iterable."""
    import streamlit as st
    from stqdm import stqdm

    from demo.src import demo_apps

    for count, value in enumerate(stqdm(values)):
        st.write(count, value)
        demo_apps.long_running_task(task_duration)


def stqdm_while_loop(length: int = 10, increment: int = 1, task_duration: float = 0.01) -> None:
    """Manually update a progress bar from a while loop."""
    from stqdm import stqdm

    from demo.src import demo_apps

    progress = stqdm(total=length)
    index = 0
    while index < length:
        index += increment
        progress.update(increment)
        demo_apps.long_running_task(task_duration)


def stqdm_backend_frontend(iterations: int = 10, task_duration: float = 0.01) -> None:
    """Compare frontend-only and backend-only progress output."""
    import streamlit as st
    from stqdm import stqdm

    from demo.src import demo_apps

    columns = st.columns(2)
    with columns[0]:
        st.write("No backend")
        for _ in stqdm(range(iterations), backend=False, frontend=True):
            demo_apps.long_running_task(task_duration)

    with columns[1]:
        st.write("No frontend")
        for _ in stqdm(range(iterations), backend=True, frontend=False):
            demo_apps.long_running_task(task_duration)


def stqdm_leave(iterations: int = 10, task_duration: float = 0.01, leave: bool | None = None) -> None:
    """Try the leave option that controls whether completed bars remain visible."""
    from threading import RLock

    import streamlit as st
    from stqdm import stqdm

    from demo.src import demo_apps

    selected_leave = st.selectbox(
        "Select leave", [True, False, None], index=0 if leave is True else 1 if leave is False else 2
    )
    stqdm.set_lock(RLock())
    for _ in stqdm(range(iterations), leave=selected_leave):
        demo_apps.long_running_task(task_duration)


def stqdm_bar_format(iterations: int = 10, task_duration: float = 0.01, bar_format: str | None = None) -> None:
    """Try several tqdm bar_format values with STqdm."""
    from threading import RLock

    import streamlit as st
    from stqdm import stqdm

    from demo.src import demo_apps

    options = ["", "{bar}", "{l_bar}{bar}{r_bar}", "{desc} {percentage:.0f}%", "blabla", None]
    index = options.index(bar_format) if bar_format in options else 2
    st.markdown(
        """
        `bar_format` controls how tqdm formats the text around the bar.

        - `None`: use the default tqdm-style progress meter.
        - `""`: keep only the bar widget, with no text.
        - `"{bar}"`: same idea as `""`, but expressed as an explicit bar placeholder.
        - `"{l_bar}{bar}{r_bar}"`: tqdm's default terminal layout, adapted to Streamlit.
        - `"{desc} {percentage:.0f}%"`: text only; no bar widget is shown.
        - `"blabla"`: plain text fallback for a template with no bar placeholder.
        """
    )
    selected_bar_format = st.selectbox("Select bar_format", options, index=index)
    stqdm.set_lock(RLock())
    for _ in stqdm(
        range(iterations),
        desc="Format",
        bar_format=selected_bar_format,
        backend=True,
        frontend=True,
    ):
        demo_apps.long_running_task(task_duration)


def stqdm_scopes(iterations: int = 5, task_duration: float = 0.01) -> None:
    """Use scoped STqdm configuration to customize nested progress bars."""
    from stqdm import stqdm

    from demo.src import demo_apps

    def run_job() -> None:
        for _ in stqdm(range(iterations)):
            demo_apps.long_running_task(task_duration)

    with stqdm.scope(frontend=True, bar_format="Hello {desc}{bar}", desc="Scoped"):
        run_job()
        with stqdm.scope(frontend=True):
            run_job()


def stqdm_last_print_t_bug(iterations: int = 10, task_duration: float = 0.01) -> None:
    """Run two consecutive STqdm bars after setting a process-safe lock."""
    from multiprocessing import RLock as ProcessRLock

    from stqdm import stqdm

    from demo.src import demo_apps

    stqdm.set_lock(ProcessRLock())
    for _ in stqdm(range(iterations)):
        demo_apps.long_running_task(task_duration)
    for _ in stqdm(range(iterations)):
        demo_apps.long_running_task(task_duration)


def stqdm_asyncio_patterns(iterations: int = 5, task_duration: float = 0.5) -> None:
    """Use STqdm with async iteration and asyncio.gather."""
    import asyncio

    import streamlit as st
    from stqdm.asyncio import stqdm_asyncio

    async def async_source():
        for index in range(iterations):
            await asyncio.sleep(task_duration)
            yield index

    async def async_job(index: int) -> int:
        await asyncio.sleep(task_duration)
        return index * 2

    async def run_async_work() -> tuple[list[int], list[int]]:
        async_items: list[int] = []
        async for item in stqdm_asyncio(async_source(), desc="Async loop", total=iterations):
            async_items.append(item)

        gathered = await stqdm_asyncio.gather(
            *(async_job(index) for index in range(iterations)),
            desc="Async gather",
        )
        return async_items, gathered

    async_items, gathered = asyncio.run(run_async_work())
    st.markdown(f"Async progress complete: loop={async_items}, gather={gathered}")


def stqdm_stop_and_retry(iterations: int = 10, task_duration: float = 0.01) -> None:
    """Show a plain Streamlit progress pattern used to compare stop-and-retry behavior."""
    import streamlit as st

    from demo.src import demo_apps

    submit = st.button("Click me")
    text_widget = st.empty()
    progress_widget = st.empty()
    if submit:
        for index in range(iterations):
            demo_apps.long_running_task(task_duration)
            text_widget.write(index)
            progress_widget.progress(index / iterations)


def stqdm_pandas(iterations: int = 10, task_duration: float = 0.01) -> None:
    """Use stqdm.pandas() to render progress for a pandas operation."""
    import pandas as pd
    from stqdm import stqdm

    from demo.src import demo_apps

    stqdm.pandas()

    def process(index: int) -> int:
        demo_apps.long_running_task(task_duration)
        return index

    pd.Series(range(iterations)).progress_map(process)


def stqdm_with_caching_and_speed(batch_size: int = 5, max_index: int = 20, task_duration: float = 0.01) -> None:
    """Combine Streamlit caching with STqdm around batched processing."""
    import streamlit as st
    from stqdm import stqdm

    from demo.src import demo_apps

    @st.cache_data
    def process_for_multiple_indexes(indexes: list[int]) -> list[int]:
        return [2 * index + 1 for index in indexes]

    for batch_start in stqdm(range(0, max_index, batch_size)):
        demo_apps.long_running_task(task_duration)
        batch_results = process_for_multiple_indexes(list(range(batch_start, batch_start + batch_size)))
        for result in batch_results:
            st.write(result)


def st_lock(task_duration: float = 0.01) -> None:
    """Store a lock in Streamlit session state and use it inside a context manager."""
    import contextlib
    from threading import RLock

    import streamlit as st

    from demo.src import demo_apps

    @contextlib.contextmanager
    def context_with_lock():
        lock_key = "_LOCK"
        if lock_key not in st.session_state:
            st.session_state[lock_key] = RLock()
            st.write("Initializing lock")
        lock = st.session_state[lock_key]
        st.write("before lock", lock)
        with lock:
            yield lock
            st.write("unlocking")

    with context_with_lock():
        st.write("in lock")
        demo_apps.long_running_task(task_duration)

    st.write("end lock")


def stqdm_patch_tqdm() -> None:
    """Patch tqdm.auto.tqdm so future tqdm.auto users render through STqdm."""
    import streamlit as st
    from tqdm import auto as module_containing_tqdm_to_patch

    from stqdm import stqdm

    if module_containing_tqdm_to_patch.tqdm is not stqdm:
        module_containing_tqdm_to_patch.tqdm = stqdm

    st.write("tqdm.auto.tqdm is patched:", module_containing_tqdm_to_patch.tqdm is stqdm)
