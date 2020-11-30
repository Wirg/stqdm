from time import sleep

import streamlit as st

from stqdm import stqdm

columns = st.beta_columns(3)
with columns[1]:
    for _ in stqdm(range(50)):
        sleep(0.5)
with columns[2]:
    for _ in stqdm(range(50)):
        sleep(0.5)
with columns[0]:
    for _ in stqdm(range(50)):
        sleep(0.5)
