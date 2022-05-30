from time import sleep

import streamlit as st
from stqdm import stqdm

for i in stqdm(i for i in range(50)):
    st.write(i)
    sleep(0.5)
