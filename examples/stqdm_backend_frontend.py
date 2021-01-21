from time import sleep

import streamlit as st

from stqdm import stqdm

columns = st.beta_columns(2)
with columns[0]:
    st.write("No backend")
    for i in stqdm(range(50), backend=False, frontend=True):
        sleep(0.5)


with columns[1]:
    st.write("No frontend")
    for i in stqdm(range(50), backend=True, frontend=False):
        sleep(0.5)
