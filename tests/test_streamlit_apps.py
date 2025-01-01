import contextlib
import datetime
from typing import Callable
from unittest import mock

import pytest
from freezegun import freeze_time
from streamlit.testing.v1.app_test import AppTest
from streamlit.testing.v1.element_tree import Block, Element

import demo.src.utils
from demo.src.demo_apps import simple_stqdm_in_main


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
        with mock.patch.object(demo.src.utils, "long_running_task", side_effect=frozen_datetime.tick):
            yield frozen_datetime


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
