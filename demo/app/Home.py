"""Demo app for stqdm.

Run this app with `streamlit run demo/app/Home.py`
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Callable

import streamlit as st

from demo.src import demo_apps


@dataclass(frozen=True)
class DemoExample:
    title: str
    description: str
    func: Callable[[], None]


EXAMPLES: tuple[DemoExample, ...] = (
    DemoExample("STqdm in main", "A standard progress bar in the main Streamlit area.", demo_apps.simple_stqdm_in_main),
    DemoExample("STqdm in sidebar", "A progress bar rendered in the Streamlit sidebar.", demo_apps.stqdm_in_sidebar),
    DemoExample("STqdm in columns", "Progress bars inside Streamlit columns.", demo_apps.stqdm_in_columns),
    DemoExample(
        "STqdm multi bars in columns",
        "Multiple column progress bars stopping at different points.",
        demo_apps.stqdm_multi_bars_in_columns,
    ),
    DemoExample("STqdm nested bars", "Nested progress bars with explicit clearing.", demo_apps.stqdm_in_main_nested),
    DemoExample("STqdm without total", "A generator example without an explicit total.", demo_apps.stqdm_no_total_no_length),
    DemoExample("STqdm with generator", "A small iterable/generator-style example.", demo_apps.stqdm_with_generator),
    DemoExample("STqdm while loop", "Manual progress updates from a while loop.", demo_apps.stqdm_while_loop),
    DemoExample(
        "STqdm backend and frontend", "Compare frontend and backend output options.", demo_apps.stqdm_backend_frontend
    ),
    DemoExample("STqdm leave option", "Control whether completed bars stay visible.", demo_apps.stqdm_leave),
    DemoExample("STqdm bar format", "Try different tqdm bar_format values.", demo_apps.stqdm_bar_format),
    DemoExample("STqdm scopes", "Use scoped default configuration.", demo_apps.stqdm_scopes),
    DemoExample("STqdm consecutive bars", "Run consecutive bars after setting a lock.", demo_apps.stqdm_last_print_t_bug),
    DemoExample("Stop and retry pattern", "A plain Streamlit progress comparison.", demo_apps.stqdm_stop_and_retry),
    DemoExample("STqdm pandas", "Use stqdm.pandas with a pandas operation.", demo_apps.stqdm_pandas),
    DemoExample(
        "STqdm caching and speed", "Combine Streamlit caching with batched progress.", demo_apps.stqdm_with_caching_and_speed
    ),
    DemoExample("Streamlit lock", "Store and use a lock in Streamlit session state.", demo_apps.st_lock),
    DemoExample("Patch tqdm.auto", "Patch tqdm.auto.tqdm to use STqdm.", demo_apps.stqdm_patch_tqdm),
)


st.set_page_config(
    layout="wide",
    page_title="STqdm Demo App",
    page_icon="ST",
    initial_sidebar_state="expanded",
)

st.title("STqdm Demo App")
st.write("Runnable documentation for STqdm examples.")
st.write("Install with `pip install stqdm`.")

selected_example = st.sidebar.selectbox("Example", EXAMPLES, format_func=lambda example: example.title)

st.title(selected_example.title)
st.write(selected_example.description)
with st.expander("Source", expanded=True):
    st.code(inspect.getsource(selected_example.func), language="python")
selected_example.func()
