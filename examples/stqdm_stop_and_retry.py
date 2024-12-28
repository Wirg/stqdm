"""
Based on https://github.com/Wirg/stqdm/issues/64#issuecomment-1250906739
There is some issue with stqdm on Windows.
Stopping this from the web frontend will create some locking issues.
You can solve this with using :

```python
from threading import RLock
from stqdm import stqdm

stqdm.set_lock(RLock())
```

See : https://github.com/Wirg/stqdm/issues/64#issuecomment-1367536561
"""

from time import sleep

import streamlit as st

submit = st.button("Click me")
text_widget = st.empty()
progress_widget = st.empty()
if submit:
    for i in range(50):
        sleep(0.5)
        text_widget.write(i)
        progress_widget.progress(i / 50)
