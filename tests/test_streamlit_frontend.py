from unittest.mock import patch
from tqdm import tqdm
from stqdm.stqdm import stqdm


def test_works_out_of_streamlit():
    for _ in stqdm(range(2)):
        pass


@patch("streamlit.empty")
def test_writes_tqdm_description(empty_mock):
    stqdmed_iterator = stqdm(range(2))
    for _ in stqdmed_iterator:
        empty_mock.return_value.write.assert_called_with(tqdm.format_meter(**{**stqdmed_iterator.format_dict, "ncols": 0}))
