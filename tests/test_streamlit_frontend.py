import asyncio
from datetime import timedelta
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time
from tqdm import tqdm

from stqdm import astqdm
from stqdm import tqdm as package_tqdm
from stqdm.asyncio import stqdm_asyncio
from stqdm.auto import tqdm as auto_tqdm
from stqdm.stqdm import IS_TEXT_INSIDE_PROGRESS_AVAILABLE, stqdm

TQDM_RUN_EVERY_ITERATION = {
    "mininterval": 0,
    "miniters": 0,
}
DESCRIPTION = "progress_bar_description"


class AsyncRange:
    def __init__(self, total: int):
        self.total = total
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= self.total:
            raise StopAsyncIteration
        value = self.index
        self.index += 1
        return value


@pytest.fixture(autouse=True, name="mock_st_empty")
def fixture_mock_st_empty():
    with patch("streamlit.empty") as st_empty:
        yield st_empty


@pytest.fixture(autouse=True, name="mock_st_container")
def fixture_mock_st_container():
    with patch("streamlit.container") as st_container:
        yield st_container


@pytest.fixture(autouse=True)
def reset_default_stqdm_config_at_the_end_of_test():
    """Reset the default config at the end of the test, to avoid tests to have side effects."""
    initial_config = stqdm.scope_stack.get_default_config()
    yield initial_config
    stqdm.scope_stack.set_default_config(initial_config)


def test_works_out_of_streamlit():
    for _ in stqdm(range(2)):
        pass


def assert_frontend_as_been_called_with(stqdmed_iterator: stqdm, text: Optional[str], progress: Optional[float]):
    """Util to test if the frontend of streamlit would have been called and in the proper condition.

    This simplify the handling of edge cases:
    - the new feature of text inside the progress bar (IS_TEXT_INSIDE_PROGRESS_AVAILABLE)
    - text & progress or only one of the two
    """
    if text is None and progress is None:
        stqdmed_iterator.st_text.write.assert_not_called()
        stqdmed_iterator.st_progress_bar.progress.assert_not_called()
    elif progress is None:
        stqdmed_iterator.st_text.write.assert_called_with(text)
        stqdmed_iterator.st_progress_bar.progress.assert_not_called()
    elif text is None:
        stqdmed_iterator.st_text.write.assert_not_called()
        stqdmed_iterator.st_progress_bar.progress.assert_called_with(progress)
    elif IS_TEXT_INSIDE_PROGRESS_AVAILABLE:
        stqdmed_iterator.st_progress_bar.progress.assert_called_with(progress, text=text)
        stqdmed_iterator.st_text.write.assert_not_called()
    else:
        stqdmed_iterator.st_text.write.assert_called_with(text)
        stqdmed_iterator.st_progress_bar.progress.assert_called_with(progress)


def test_default_stqdm():
    stqdmed_iterator = stqdm(range(2), **TQDM_RUN_EVERY_ITERATION)
    for i, _ in enumerate(stqdmed_iterator):
        assert_frontend_as_been_called_with(
            stqdmed_iterator,
            text=tqdm.format_meter(**{**stqdmed_iterator.format_dict, "ncols": 0}),
            progress=i / len(stqdmed_iterator),
        )


def test_writes_tqdm_description_when_no_length_but_total():
    stqdmed_iterator = stqdm((i for i in range(2)), total=3, **TQDM_RUN_EVERY_ITERATION)
    for i, _ in enumerate(stqdmed_iterator):
        assert_frontend_as_been_called_with(
            stqdmed_iterator,
            text=tqdm.format_meter(**{**stqdmed_iterator.format_dict, "ncols": 0}),
            progress=i / 3,
        )


def test_writes_tqdm_description_when_no_length_no_total():
    stqdmed_iterator = stqdm((i for i in range(2)), **TQDM_RUN_EVERY_ITERATION)

    for _ in stqdmed_iterator:
        assert_frontend_as_been_called_with(
            stqdmed_iterator,
            text=tqdm.format_meter(**{**stqdmed_iterator.format_dict, "ncols": 0}),
            progress=None,
        )


def test_issue_104_backend_false_does_not_emit_console_output(capsys):
    for _ in stqdm(range(2), backend=False, frontend=True, **TQDM_RUN_EVERY_ITERATION):
        pass

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


@pytest.mark.parametrize(
    "bar_format,get_text",
    [
        (None, lambda i, total: tqdm.format_meter(n=i, total=total, elapsed=i, ncols=0, prefix=DESCRIPTION)),
        ("", lambda i, total: None),
        ("{bar}", lambda i, total: None),
        (
            "{bar}{desc}",
            lambda i, total: tqdm.format_meter(n=i, total=total, elapsed=i, bar_format="{desc}", prefix=DESCRIPTION),
        ),
        (
            "{l_bar}{bar}{r_bar}",
            lambda i, total: tqdm.format_meter(n=i, total=total, elapsed=i, bar_format="{l_bar}{r_bar}", prefix=DESCRIPTION),
        ),
    ],
)
def test_bar_format(bar_format, get_text):
    with freeze_time("2020-01-01") as frozen_time:
        stqdmed_iterator = stqdm(range(2), bar_format=bar_format, desc=DESCRIPTION, **TQDM_RUN_EVERY_ITERATION)
        for i, _ in enumerate(stqdmed_iterator):
            frozen_time.tick(timedelta(seconds=1))
            assert_frontend_as_been_called_with(
                stqdmed_iterator,
                text=get_text(i=i, total=2),
                progress=i / len(stqdmed_iterator),
            )


def test_backend_format_is_not_rewritten_by_frontend_compatibility():
    with patch.object(tqdm, "display") as tqdm_display_mock:
        stqdmed_iterator = stqdm(
            range(2), bar_format="{l_bar}{bar}{r_bar}", backend=True, frontend=False, **TQDM_RUN_EVERY_ITERATION
        )
        for _ in stqdmed_iterator:
            pass

    assert stqdmed_iterator.format_dict["bar_format"] == "{l_bar}{bar}{r_bar}"
    tqdm_display_mock.assert_called()


def test_leave_false_keeps_stqdm():
    # pylint: disable=protected-access
    stqdmed_iterator = stqdm(range(2), leave=True)
    mock_progress_bar = MagicMock()
    mock_text = MagicMock()
    stqdmed_iterator._st_progress_bar = mock_progress_bar
    stqdmed_iterator._st_text = mock_text
    for _ in stqdmed_iterator:
        pass
    assert stqdmed_iterator._st_progress_bar is mock_progress_bar
    mock_progress_bar.empty.assert_not_called()
    assert stqdmed_iterator._st_text is mock_text
    mock_text.empty.assert_not_called()


def test_leave_true_remove_stqdm():
    # pylint: disable=protected-access
    stqdmed_iterator = stqdm(range(2), leave=False)
    mock_progress_bar = MagicMock()
    mock_text = MagicMock()
    stqdmed_iterator._st_progress_bar = mock_progress_bar
    stqdmed_iterator._st_text = mock_text
    for _ in stqdmed_iterator:
        pass
    assert stqdmed_iterator._st_progress_bar is None
    mock_progress_bar.empty.assert_called_once()
    assert stqdmed_iterator._st_text is None
    mock_text.empty.assert_called_once()


@pytest.mark.parametrize("frontend", [True, False])
@pytest.mark.parametrize("backend", [True, False])
@patch.object(stqdm, "st_display")
@patch.object(tqdm, "display")
def test_use_stqdm_frontend_backend(tqdm_display_mock, st_display_mock, backend, frontend):
    # pylint: disable=protected-access
    stqdmed_iterator = stqdm(range(2), backend=backend, frontend=frontend, **TQDM_RUN_EVERY_ITERATION)
    for _ in stqdmed_iterator:
        pass
    if backend:
        tqdm_display_mock.assert_called()
    else:
        tqdm_display_mock.assert_not_called()
    if frontend:
        st_display_mock.assert_called()
    else:
        st_display_mock.assert_not_called()


def test_stqdm_change_default_config(mock_st_empty, mock_st_container):
    test_default_stqdm()
    mock_st_empty.reset_mock()
    mock_st_container.reset_mock()
    stqdm.set_default_config(frontend=False)
    stqdmed_iterator = stqdm(range(2), **TQDM_RUN_EVERY_ITERATION)
    for _ in enumerate(stqdmed_iterator):
        assert_frontend_as_been_called_with(
            stqdmed_iterator,
            text=None,
            progress=None,
        )
    mock_st_empty.reset_mock()
    mock_st_container.reset_mock()
    stqdm.set_default_config(bar_format="{desc}", desc="hello")
    stqdmed_iterator = stqdm(range(2), **TQDM_RUN_EVERY_ITERATION)
    for _ in enumerate(stqdmed_iterator):
        assert_frontend_as_been_called_with(
            stqdmed_iterator,
            text="hello",
            progress=None,
        )


def test_stqdm_test_scope(mock_st_container, mock_st_empty):
    with stqdm.scope(frontend=False):
        stqdmed_iterator = stqdm(range(2), **TQDM_RUN_EVERY_ITERATION)
        for _ in enumerate(stqdmed_iterator):
            assert_frontend_as_been_called_with(
                stqdmed_iterator,
                text=None,
                progress=None,
            )
    mock_st_container.reset_mock()
    mock_st_empty.reset_mock()
    with stqdm.scope(bar_format="{desc}", desc="hello"):
        stqdmed_iterator = stqdm(range(2), **TQDM_RUN_EVERY_ITERATION)
        for _ in enumerate(stqdmed_iterator):
            assert_frontend_as_been_called_with(
                stqdmed_iterator,
                text="hello",
                progress=None,
            )
    mock_st_container.reset_mock()
    mock_st_empty.reset_mock()
    test_default_stqdm()


def test_stqdm_nested_scope_inherits_outer_bar_format():
    with stqdm.scope(bar_format="{desc}", desc="outer"):
        with stqdm.scope(frontend=True):
            stqdmed_iterator = stqdm(range(2), **TQDM_RUN_EVERY_ITERATION)
            for _ in enumerate(stqdmed_iterator):
                assert_frontend_as_been_called_with(
                    stqdmed_iterator,
                    text="outer",
                    progress=None,
                )


def test_stqdm_nested_scope_explicit_none_resets_outer_bar_format(mock_st_empty, mock_st_container):
    with stqdm.scope(bar_format="{desc}", desc="outer"):
        with stqdm.scope(bar_format=None):
            stqdmed_iterator = stqdm(range(2), **TQDM_RUN_EVERY_ITERATION)
            for i, _ in enumerate(stqdmed_iterator):
                assert_frontend_as_been_called_with(
                    stqdmed_iterator,
                    text=tqdm.format_meter(**{**stqdmed_iterator.format_dict, "ncols": 0}),
                    progress=i / len(stqdmed_iterator),
                )

    mock_st_empty.reset_mock()
    mock_st_container.reset_mock()
    test_default_stqdm()


def test_stqdm_nested_scope_empty_bar_format_hides_text_but_keeps_bar(mock_st_empty, mock_st_container):
    with stqdm.scope(bar_format="{desc}", desc="outer"):
        with stqdm.scope(bar_format=""):
            stqdmed_iterator = stqdm(range(2), **TQDM_RUN_EVERY_ITERATION)
            for i, _ in enumerate(stqdmed_iterator):
                assert_frontend_as_been_called_with(
                    stqdmed_iterator,
                    text=None,
                    progress=i / len(stqdmed_iterator),
                )

    mock_st_empty.reset_mock()
    mock_st_container.reset_mock()
    test_default_stqdm()


def test_stqdm_call_kwargs_override_nested_scope_with_none(mock_st_empty, mock_st_container):
    with stqdm.scope(bar_format="{desc}", desc="outer"):
        with stqdm.scope(desc="inner"):
            stqdmed_iterator = stqdm(range(2), bar_format=None, **TQDM_RUN_EVERY_ITERATION)
            for i, _ in enumerate(stqdmed_iterator):
                assert_frontend_as_been_called_with(
                    stqdmed_iterator,
                    text=tqdm.format_meter(**{**stqdmed_iterator.format_dict, "ncols": 0}),
                    progress=i / len(stqdmed_iterator),
                )

    mock_st_empty.reset_mock()
    mock_st_container.reset_mock()
    test_default_stqdm()


def test_stqdm_three_nested_scopes_merge_outer_to_inner(mock_st_empty, mock_st_container):
    with stqdm.scope(bar_format="{desc}", desc="outer", frontend=True):
        with stqdm.scope(desc="middle"):
            with stqdm.scope(backend=False):
                stqdmed_iterator = stqdm(range(2), **TQDM_RUN_EVERY_ITERATION)
                for _ in enumerate(stqdmed_iterator):
                    assert_frontend_as_been_called_with(
                        stqdmed_iterator,
                        text="middle",
                        progress=None,
                    )

    mock_st_empty.reset_mock()
    mock_st_container.reset_mock()
    test_default_stqdm()


def test_stqdm_arbitrary_tqdm_kwargs_inherit_through_nested_scopes():
    with stqdm.scope(unit="items", dynamic_ncols=True):
        with stqdm.scope(desc="inner"):
            assert stqdm.combine_default_and_provided_kwargs({}) == {
                "unit": "items",
                "dynamic_ncols": True,
                "desc": "inner",
            }


def test_stqdm_inner_frontend_override_keeps_outer_format_values():
    with stqdm.scope(bar_format="{desc}", desc="outer", frontend=True):
        with stqdm.scope(frontend=False):
            assert stqdm.combine_default_and_provided_kwargs({}) == {
                "bar_format": "{desc}",
                "desc": "outer",
                "frontend": False,
            }


def test_stqdm_default_config_add_description():
    stqdm.set_default_config(bar_format="{desc}", desc="hello")
    stqdmed_iterator = stqdm(range(2), **TQDM_RUN_EVERY_ITERATION)
    for _ in enumerate(stqdmed_iterator):
        assert_frontend_as_been_called_with(
            stqdmed_iterator,
            text="hello",
            progress=None,
        )


def test_astqdm_alias_points_to_async_entrypoint():
    assert astqdm is stqdm_asyncio


def test_auto_alias_points_to_async_entrypoint():
    assert auto_tqdm is stqdm_asyncio


def test_package_root_tqdm_alias_points_to_async_entrypoint():
    assert package_tqdm is stqdm_asyncio


@pytest.mark.parametrize("iterable_factory", [lambda: range(2), lambda: AsyncRange(2)])
def test_stqdm_asyncio_supports_sync_and_async_iterables(iterable_factory):
    async def consume():
        stqdmed_iterator = stqdm_asyncio(iterable_factory(), total=2, **TQDM_RUN_EVERY_ITERATION)
        seen = []
        index = 0
        async for item in stqdmed_iterator:
            seen.append(item)
            assert_frontend_as_been_called_with(
                stqdmed_iterator,
                text=tqdm.format_meter(**{**stqdmed_iterator.format_dict, "ncols": 0}),
                progress=(index + 1) / len(stqdmed_iterator),
            )
            index += 1
        return seen

    assert asyncio.run(consume()) == [0, 1]


def test_stqdm_asyncio_as_completed_uses_progress_bar():
    async def collect():
        async def delayed_result(value: int, delay: float) -> int:
            await asyncio.sleep(delay)
            return value

        tasks = [delayed_result(1, 0.02), delayed_result(2, 0.01)]
        return [await future for future in stqdm_asyncio.as_completed(tasks, total=2, **TQDM_RUN_EVERY_ITERATION)]

    with patch.object(stqdm_asyncio, "st_display") as st_display_mock:
        assert asyncio.run(collect()) == [2, 1]

    st_display_mock.assert_called()


def test_stqdm_asyncio_supports_dual_protocol_iterables():
    class DualProtocolIterator:
        def __init__(self, values):
            self.values = iter(values)

        def __iter__(self):
            return self

        def __next__(self):
            return next(self.values)

        def __aiter__(self):
            return self

        async def __anext__(self):
            return next(self.values)

    async def consume():
        return [item async for item in stqdm_asyncio(DualProtocolIterator([0, 1]), total=2, **TQDM_RUN_EVERY_ITERATION)]

    assert asyncio.run(consume()) == [0, 1]


def test_stqdm_asyncio_gather_returns_results_in_input_order():
    async def collect():
        async def delayed_result(value: int, delay: float) -> int:
            await asyncio.sleep(delay)
            return value

        return await stqdm_asyncio.gather(
            delayed_result(1, 0.02),
            delayed_result(2, 0.01),
            total=2,
            **TQDM_RUN_EVERY_ITERATION,
        )

    with patch.object(stqdm_asyncio, "st_display") as st_display_mock:
        assert asyncio.run(collect()) == [1, 2]

    st_display_mock.assert_called()
