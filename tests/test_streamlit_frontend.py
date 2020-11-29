from unittest.mock import patch
from tqdm import tqdm
from stqdm.stqdm import stqdm


@patch("streamlit.empty")
def test_write_tqdm_description(empty_mock):
    stqdmed_iterator = stqdm(range(2))
    for _ in stqdmed_iterator:
        empty_mock.return_value.write.assert_called_with(tqdm.format_meter(**{**stqdmed_iterator.format_dict, "ncols": 0}))
