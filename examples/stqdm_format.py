from time import sleep

import streamlit as st

from stqdm import stqdm

bar_format = st.selectbox(
    "Select bar_format", ["", "{bar}", "{l_bar}{bar}{r_bar}", "{desc} {percentage:.0f}%", "blabla", None]
)

empty = st.container()

for item in stqdm(range(10), bar_format=bar_format, st_container=empty):
    sleep(0.5)
