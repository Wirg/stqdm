from __future__ import annotations

import inspect
from dataclasses import dataclass
from textwrap import dedent
from typing import Callable

import streamlit as st

from demo.src import demo_apps


@dataclass(frozen=True)
class DemoPage:
    section: str
    title: str
    description: str
    function: Callable[..., None]
    kwargs: dict[str, object]
    default: bool = False


def render_demo(page: DemoPage) -> None:
    st.title(page.title)
    st.caption(page.description)
    st.code(dedent(inspect.getsource(page.function)).strip(), language="python")
    st.divider()
    page.function(**page.kwargs)


def build_page(page: DemoPage) -> st.Page:
    def run_page() -> None:
        render_demo(page)

    return st.Page(run_page, title=page.title, url_path=page.function.__name__, default=page.default)


DEMO_PAGES: tuple[DemoPage, ...] = (
    DemoPage(
        section="Basics",
        title="Use stqdm in the main area",
        description="The basic `for` loop pattern with an explicit total.",
        function=demo_apps.simple_stqdm_in_main,
        kwargs={"stop_iterations": 10, "total_iterations": 50, "task_duration": 0.01},
        default=True,
    ),
    DemoPage(
        section="Basics",
        title="Use stqdm in the sidebar",
        description="Render the bar inside `st.sidebar`.",
        function=demo_apps.stqdm_in_sidebar,
        kwargs={"iterations": 10, "task_duration": 0.01},
    ),
    DemoPage(
        section="Basics",
        title="Use stqdm in columns",
        description="Place several independent bars in a multi-column layout.",
        function=demo_apps.stqdm_in_columns,
        kwargs={"iterations": 10, "task_duration": 0.01},
    ),
    DemoPage(
        section="Basics",
        title="Multiple bars in columns",
        description="Stop each column at a different point.",
        function=demo_apps.stqdm_multi_bars_in_columns,
        kwargs={"iterations": 10, "task_duration": 0.01},
    ),
    DemoPage(
        section="Basics",
        title="Nested progress bars",
        description="Render nested bars and clear the inner one after each run.",
        function=demo_apps.stqdm_in_main_nested,
        kwargs={"outer_iterations": 3, "inner_iterations": 4, "task_duration": 0.01},
    ),
    DemoPage(
        section="Basics",
        title="Iterables without a total",
        description="Use a generator with no known length.",
        function=demo_apps.stqdm_no_total_no_length,
        kwargs={"iterations": 10, "task_duration": 0.01},
    ),
    DemoPage(
        section="Basics",
        title="Generator values",
        description="Iterate over a small generator-like iterable.",
        function=demo_apps.stqdm_with_generator,
        kwargs={"values": ("a", "b", "c"), "task_duration": 0.01},
    ),
    DemoPage(
        section="Basics",
        title="While loop updates",
        description="Update the progress bar manually in a loop.",
        function=demo_apps.stqdm_while_loop,
        kwargs={"length": 10, "increment": 1, "task_duration": 0.01},
    ),
    DemoPage(
        section="Configuration",
        title="Frontend and backend output",
        description="Compare frontend-only and backend-only rendering.",
        function=demo_apps.stqdm_backend_frontend,
        kwargs={"iterations": 10, "task_duration": 0.01},
    ),
    DemoPage(
        section="Configuration",
        title="Leave behavior",
        description="Compare how completed bars stay visible or disappear.",
        function=demo_apps.stqdm_leave,
        kwargs={"iterations": 10, "task_duration": 0.01, "leave": None},
    ),
    DemoPage(
        section="Configuration",
        title="bar_format values",
        description="Try a few tqdm bar format strings.",
        function=demo_apps.stqdm_bar_format,
        kwargs={"iterations": 10, "task_duration": 0.01, "bar_format": None},
    ),
    DemoPage(
        section="Configuration",
        title="Scoped configuration",
        description="Use `stqdm.scope()` to override nested defaults temporarily.",
        function=demo_apps.stqdm_scopes,
        kwargs={"iterations": 5, "task_duration": 0.01},
    ),
    DemoPage(
        section="Configuration",
        title="last_print_t bug",
        description="Run two consecutive bars after setting a process-safe lock.",
        function=demo_apps.stqdm_last_print_t_bug,
        kwargs={"iterations": 10, "task_duration": 0.01},
    ),
    DemoPage(
        section="Configuration",
        title="Patch tqdm.auto",
        description="Patch `tqdm.auto.tqdm` so future callers use STqdm.",
        function=demo_apps.stqdm_patch_tqdm,
        kwargs={},
    ),
    DemoPage(
        section="Patterns",
        title="Stop and retry",
        description="A plain Streamlit pattern for comparison.",
        function=demo_apps.stqdm_stop_and_retry,
        kwargs={"iterations": 10, "task_duration": 0.01},
    ),
    DemoPage(
        section="Patterns",
        title="Async progress patterns",
        description="Use `stqdm` with async iteration and `asyncio.gather()`.",
        function=demo_apps.stqdm_asyncio_patterns,
        kwargs={"iterations": 5, "task_duration": 0.5},
    ),
    DemoPage(
        section="Patterns",
        title="Pandas integration",
        description="Use `stqdm.pandas()` with a pandas `Series`.",
        function=demo_apps.stqdm_pandas,
        kwargs={"iterations": 10, "task_duration": 0.01},
    ),
    DemoPage(
        section="Patterns",
        title="Caching and speed",
        description="Combine caching with batched processing.",
        function=demo_apps.stqdm_with_caching_and_speed,
        kwargs={"batch_size": 5, "max_index": 20, "task_duration": 0.01},
    ),
    DemoPage(
        section="Patterns",
        title="Session-state lock",
        description="Store a lock in session state and reuse it across calls.",
        function=demo_apps.st_lock,
        kwargs={"task_duration": 0.01},
    ),
)


def main() -> None:
    st.set_page_config(page_title="stqdm demos", layout="wide")
    navigation = st.navigation(
        {
            section: [build_page(page) for page in DEMO_PAGES if page.section == section]
            for section in ("Basics", "Configuration", "Patterns")
        }
    )
    navigation.run()


main()
