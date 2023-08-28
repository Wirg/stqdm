import time

import streamlit as st

from stqdm import stqdm


class Slow:
    def __init__(self, n_iterations: int):
        self._n_iterations = n_iterations

    def __len__(self):
        return self._n_iterations

    def __iter__(self):
        for i in range(self._n_iterations):
            time.sleep(0.0005)
            yield i


def example_run(test1, test2):
    total_iterations = len(test1) + len(test2)
    with stqdm(total=total_iterations, desc="Calculating...", mininterval=0.1) as pbar:
        for _ in test1:
            pbar.update(1)
        for _ in test2:
            pbar.update(1)


if st.button("Exemple"):
    with st.spinner("Processing..."):
        example_run(Slow(1500), Slow(2000))
