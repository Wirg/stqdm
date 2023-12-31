from typing import Optional
from unittest.mock import patch

from tqdm import tqdm

from stqdm.stqdm import IS_TEXT_INSIDE_PROGRESS_AVAILABLE, stqdm

TQDM_RUN_EVERY_ITERATION = {
    "mininterval": 0,
    "miniters": 0,
}


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
