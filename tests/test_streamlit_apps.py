import contextlib
import datetime
from typing import Callable
from unittest import mock

import pytest
from freezegun import freeze_time
from streamlit.testing.v1.app_test import AppTest
from streamlit.testing.v1.element_tree import Block, Element

from demo.src.demo_apps import simple_stqdm_in_main, stqdm_bar_format, stqdm_scopes

pytestmark = pytest.mark.demo_app


def collect_block_elements(block: Block, should_take: Callable[[Element], bool]) -> list[Element]:
    children = block.children.values()
    results: list[Element] = []
    for child in children:
        if isinstance(child, Element):
            if should_take(child):
                results.append(child)
        elif isinstance(child, Block):
            results.extend(collect_block_elements(child, should_take))
        else:
            raise TypeError(f"Unexpected child type: {type(child)}")
    return results


@contextlib.contextmanager
def freeze_time_and_mock_long_running_task(original_date: str):
    """A context manager that uses freezegun to freeze time and mock the long_running_task function."""
    with freeze_time(original_date, ignore=["streamlit"]) as frozen_datetime:
        with mock.patch("demo.src.demo_apps.long_running_task", side_effect=frozen_datetime.tick):
            yield frozen_datetime


ISSUE_101_NESTED_LOOPS_SCRIPT = """
from functools import partial

import streamlit as st
from stqdm import stqdm

progress = partial(stqdm, st_container=st.sidebar)


def subfun(total: int) -> None:
    for _ in progress(range(total), desc="paragraph"):
        pass


sections = "ABCDEFGHIJK"
with progress(total=len(sections), desc="Working on") as pbar:
    for section_counter, draft_section in enumerate(sections):
        pbar.update(section_counter)
        pbar.set_description(desc=f"Section '{draft_section}'")
        subfun(3)
"""


ISSUE_98_TWO_STQDM_INSTANCES_SCRIPT = """
from stqdm import stqdm

for _ in stqdm(range(2)):
    pass

for _ in stqdm(range(2)):
    pass
"""


@pytest.mark.parametrize("stop_iterations,total_iterations,task_duration", [(10, 50, 5), (13, 25, 3), (0, 50, 5), (50, 50, 2)])
def test_progress(stop_iterations: int, total_iterations: int, task_duration: float):
    with freeze_time_and_mock_long_running_task("2024-01-01"):
        app_test = AppTest.from_function(
            simple_stqdm_in_main,
            kwargs={"stop_iterations": stop_iterations, "total_iterations": total_iterations, "task_duration": task_duration},
        )
        app_test.run(timeout=3)
    assert not app_test.exception
    progress_bars = collect_block_elements(app_test.main, should_take=lambda element: element.type == "progress")
    assert len(progress_bars) == 1
    assert progress_bars[0].value == round(100 * stop_iterations / total_iterations)
    if stop_iterations == 0:
        assert progress_bars[0].text == f"0% 0/{total_iterations} [00:00<?, ?it/s]"
    else:
        task_duration_time = datetime.timedelta(seconds=task_duration)
        elapsed = str(stop_iterations * task_duration_time)[-5:]
        remaining = str((total_iterations - stop_iterations) * task_duration_time)[-5:]
        assert (
            progress_bars[0].text
            # pylint: disable=line-too-long
            == f"{stop_iterations / total_iterations:.0%} {stop_iterations}/{total_iterations} [{elapsed}<{remaining},  {task_duration:.2f}s/it]"
        )


def test_single_entrypoint_renders_with_app_test():
    with freeze_time_and_mock_long_running_task("2024-01-01"):
        app_test = AppTest.from_file("demo/app/Home.py")
        app_test.run(timeout=5)

    assert not app_test.exception


@pytest.mark.parametrize(
    "bar_format,expected_kind,expected_text",
    [
        (None, "progress", "Format"),
        ("", "progress", ""),
        ("{bar}", "progress", ""),
        ("{l_bar}{bar}{r_bar}", "progress", "Format"),
        ("{desc} {percentage:.0f}%", "markdown", "Format 100%"),
    ],
)
def test_bar_format_demo_renders_expected_output(bar_format: str | None, expected_kind: str, expected_text: str):
    with freeze_time_and_mock_long_running_task("2024-01-01"):
        app_test = AppTest.from_function(
            stqdm_bar_format,
            kwargs={"iterations": 3, "task_duration": 0.0, "bar_format": bar_format},
        )
        app_test.run(timeout=5)

    assert not app_test.exception
    assert any(
        "controls how tqdm formats the text around the bar"
        in str(getattr(element, "text", None) or getattr(element, "value", ""))
        for element in collect_block_elements(app_test.main, should_take=lambda element: element.type == "markdown")
    )
    assert len(app_test.selectbox) == 1
    assert app_test.selectbox[0].value == bar_format

    collected = collect_block_elements(app_test.main, should_take=lambda element: element.type == expected_kind)
    if expected_kind == "markdown":
        assert len(collected) >= 1
        assert any(
            expected_text in str(getattr(element, "text", None) or getattr(element, "value", "")) for element in collected
        )
    else:
        assert len(collected) == 1
        actual_text = getattr(collected[0], "text", None)
        if actual_text is None:
            actual_text = getattr(collected[0], "value", None)
        assert expected_text in str(actual_text or "")


def test_scoped_configuration_demo_renders_description():
    with freeze_time_and_mock_long_running_task("2024-01-01"):
        app_test = AppTest.from_function(stqdm_scopes, kwargs={"iterations": 2, "task_duration": 0.0})
        app_test.run(timeout=5)

    assert not app_test.exception
    progress_bars = collect_block_elements(app_test.main, should_take=lambda element: element.type == "progress")
    assert len(progress_bars) >= 2
    assert any("Hello Scoped" in getattr(progress_bar, "text", "") for progress_bar in progress_bars)


def test_issue_101_nested_loops_do_not_raise_streamlit_api_exception():
    with freeze_time_and_mock_long_running_task("2024-01-01"):
        app_test = AppTest.from_string(ISSUE_101_NESTED_LOOPS_SCRIPT)
        app_test.run(timeout=5)

    assert not app_test.exception
    progress_bars = collect_block_elements(app_test.main, should_take=lambda element: element.type == "progress")
    progress_bars.extend(collect_block_elements(app_test.sidebar, should_take=lambda element: element.type == "progress"))
    assert len(progress_bars) >= 2
    assert all(0 <= progress_bar.value <= 100 for progress_bar in progress_bars)


def test_issue_98_two_stqdm_instances_survive_reruns():
    with freeze_time_and_mock_long_running_task("2024-01-01"):
        app_test = AppTest.from_string(ISSUE_98_TWO_STQDM_INSTANCES_SCRIPT)
        app_test.run(timeout=5)
        app_test.run(timeout=5)

    assert not app_test.exception
    progress_bars = collect_block_elements(app_test.main, should_take=lambda element: element.type == "progress")
    assert len(progress_bars) >= 1
