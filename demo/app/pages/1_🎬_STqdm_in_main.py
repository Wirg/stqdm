# pylint: disable=invalid-name,non-ascii-file-name
import inspect

import streamlit as st

from demo.src.demo_apps import simple_stqdm_in_main

st.markdown(simple_stqdm_in_main.__doc__)
st.code(inspect.getsource(simple_stqdm_in_main))

simple_stqdm_in_main(stop_iterations=10, total_iterations=50, task_duration=0.5)
