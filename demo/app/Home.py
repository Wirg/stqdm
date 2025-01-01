"""Demo app for stqdm.

Run this app with `streamlit run demo/Home.py`
"""

# pylint: disable=invalid-name,non-ascii-file-name

import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="STqdm Demo App",
    page_icon="🎈",
    initial_sidebar_state="expanded",
)

st.markdown(
    """\
# Demo app for STqdm.

This is the demo application for stqdm.

Install with `pip install stqdm`.
"""
)
