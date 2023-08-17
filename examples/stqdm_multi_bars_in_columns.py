from time import sleep

import streamlit as st

from stqdm import stqdm

columns = st.columns(3)
with columns[1]:
    for i in stqdm(range(50)):
        sleep(0.5)
        if i == 20:
            break
with columns[2]:
    for i in stqdm(range(50)):
        sleep(0.5)
        if i == 30:
            break
with columns[0]:
    for i in stqdm(range(50)):
        sleep(0.5)
        if i == 15:
            break
