from time import sleep

import streamlit as st

from stqdm import stqdm

leave = st.checkbox("Should leave progress bar")

for _ in stqdm(range(10), leave=leave):
    sleep(0.1)
