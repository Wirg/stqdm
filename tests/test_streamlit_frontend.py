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


def test_works_out_of_streamlit():
    for _ in stqdm(range(2)):
        pass


def assert_frontend_as_been_called_with(stqdmed_iterator: stqdm, text: Optional[str], progress: Optional[float]):
    if text is None and progress is None:
        raise ValueError("Nothing to assert.")
    if progress is None:
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


@patch("streamlit.empty")
def test_writes_tqdm_description(_):
    stqdmed_iterator = stqdm(range(2), **TQDM_RUN_EVERY_ITERATION)
    for i, _ in enumerate(stqdmed_iterator):
        assert_frontend_as_been_called_with(
            stqdmed_iterator,
            text=tqdm.format_meter(**{**stqdmed_iterator.format_dict, "ncols": 0}),
            progress=i / len(stqdmed_iterator),
        )


@patch("streamlit.empty")
def test_writes_tqdm_description_when_no_length_but_total(_):
    stqdmed_iterator = stqdm((i for i in range(2)), total=3, **TQDM_RUN_EVERY_ITERATION)
    for i, _ in enumerate(stqdmed_iterator):
        assert_frontend_as_been_called_with(
            stqdmed_iterator,
            text=tqdm.format_meter(**{**stqdmed_iterator.format_dict, "ncols": 0}),
            progress=i / 3,
        )


@patch("streamlit.empty")
def test_writes_tqdm_description_when_no_length_no_total(_):
    stqdmed_iterator = stqdm((i for i in range(2)), **TQDM_RUN_EVERY_ITERATION)

    for _ in stqdmed_iterator:
        assert_frontend_as_been_called_with(
            stqdmed_iterator,
            text=tqdm.format_meter(**{**stqdmed_iterator.format_dict, "ncols": 0}),
            progress=None,
        )


@patch("streamlit.empty")
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
def test_bar_format(_, bar_format, get_text):
    with freeze_time("2020-01-01") as frozen_time:
        stqdmed_iterator = stqdm(range(2), bar_format=bar_format, **TQDM_RUN_EVERY_ITERATION, desc=DESCRIPTION)
        for i, _ in enumerate(stqdmed_iterator):
            frozen_time.tick(timedelta(seconds=1))
            assert_frontend_as_been_called_with(
                stqdmed_iterator,
                text=get_text(i=i, total=2),
                progress=i / len(stqdmed_iterator),
            )


@patch("streamlit.empty")
def test_leave_false_keeps_stqdm(_):
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


@patch("streamlit.empty")
def test_leave_true_remove_stqdm(_):
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
