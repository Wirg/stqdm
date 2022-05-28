from unittest.mock import patch

from tqdm import tqdm

from stqdm.stqdm import stqdm


TQDM_RUN_EVERY_ITERATION = {
    "mininterval": 0,
    "miniters": 0,
}


def test_works_out_of_streamlit():
    for _ in stqdm(range(2)):
        pass


@patch("streamlit.empty")
def test_writes_tqdm_description(_):
    stqdmed_iterator = stqdm(range(2), **TQDM_RUN_EVERY_ITERATION)
    for i, _ in enumerate(stqdmed_iterator):
        stqdmed_iterator.st_text.write.assert_called_with(tqdm.format_meter(**{**stqdmed_iterator.format_dict, "ncols": 0}))
        stqdmed_iterator.st_progress_bar.progress.assert_called_with(i / len(stqdmed_iterator))


@patch("streamlit.empty")
def test_writes_tqdm_description_when_no_length_but_total(_):
    stqdmed_iterator = stqdm((i for i in range(2)), total=2, **TQDM_RUN_EVERY_ITERATION)
    for i, _ in enumerate(stqdmed_iterator):
        stqdmed_iterator.st_text.write.assert_called_with(tqdm.format_meter(**{**stqdmed_iterator.format_dict, "ncols": 0}))
        stqdmed_iterator.st_progress_bar.progress.assert_called_with(i / len(stqdmed_iterator))


@patch("streamlit.empty")
def test_writes_tqdm_description_when_no_length_no_total(_):
    stqdmed_iterator = stqdm((i for i in range(2)), **TQDM_RUN_EVERY_ITERATION)

    for _ in stqdmed_iterator:
        stqdmed_iterator.st_text.write.assert_called_with(tqdm.format_meter(**{**stqdmed_iterator.format_dict, "ncols": 0}))
        stqdmed_iterator.st_progress_bar.progress.assert_not_called()
