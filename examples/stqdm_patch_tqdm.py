from time import sleep

import streamlit as st
from tqdm import tqdm

from stqdm.stqdm import stqdm


def loop():
    for _ in tqdm(range(10)):
        sleep(0.5)
    st.markdown("________")


with st.echo():
    stqdm.tqdm_start(backend=True)
    loop()

with st.echo():
    stqdm.tqdm_start(frontend=False)
    loop()

with st.echo():
    stqdm.tqdm_start(backend=False)
    loop()

with st.echo():
    stqdm.tqdm_start(st_container=st.sidebar)
    loop()


st.write("end")
