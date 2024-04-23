from datetime import timedelta
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time
from tqdm import tqdm

from stqdm.stqdm import IS_TEXT_INSIDE_PROGRESS_AVAILABLE, stqdm

TQDM_RUN_EVERY_ITERATION = {
    "mininterval": 0,
    "miniters": 0,
}
DESCRIPTION = "progress_bar_description"


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


@pytest.mark.parametrize(
    "bar_format,get_text",
    [
        (None, lambda i, total: tqdm.format_meter(n=i, total=total, elapsed=i, ncols=0, prefix=DESCRIPTION)),
        ("{bar}", lambda i, total: None),
        (
            "{bar}{desc}",
            lambda i, total: tqdm.format_meter(n=i, total=total, elapsed=i, bar_format="{desc}", prefix=DESCRIPTION),
        ),
    ],
)
def test_bar_format(bar_format, get_text):
    with freeze_time("2020-01-01") as frozen_time:
        stqdmed_iterator = stqdm(range(2), bar_format=bar_format, **TQDM_RUN_EVERY_ITERATION, desc=DESCRIPTION)
        for i, _ in enumerate(stqdmed_iterator):
            frozen_time.tick(timedelta(seconds=1))
            assert_frontend_as_been_called_with(
                stqdmed_iterator,
                text=get_text(i=i, total=2),
                progress=i / len(stqdmed_iterator),
            )


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


def test_stqdm_default_config_add_description():
    stqdm.set_default_config(bar_format="{desc}", desc="hello")
    stqdmed_iterator = stqdm(range(2), **TQDM_RUN_EVERY_ITERATION)
    for _ in enumerate(stqdmed_iterator):
        assert_frontend_as_been_called_with(
            stqdmed_iterator,
            text="hello",
            progress=None,
        )
