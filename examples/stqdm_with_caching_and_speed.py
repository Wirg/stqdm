"""
How to cache response.
This is a base streamlit util not related to stqdm.
See : https://docs.streamlit.io/library/advanced-features/caching

From : https://discuss.streamlit.io/t/stqdm-a-tqdm-like-progress-bar-for-streamlit/10097/20?u=wirg
"""

from time import sleep
from typing import List

import streamlit as st

from stqdm import stqdm


def process_for_index(index: int) -> int:
    sleep(0.05)
    return 2 * index + 1


@st.cache  # Use streamlit to cache the results of this function for i
def process_for_multiple_indexes(indexes: List[int]) -> List[int]:
    return [process_for_index(index) for index in indexes]


BATCH_SIZE = 500

for batch_start in stqdm(range(0, 5000, BATCH_SIZE)):
    batch_results = process_for_multiple_indexes(list(range(batch_start, batch_start + BATCH_SIZE)))
    for result in batch_results:
        st.write(result)
