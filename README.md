# stqdm
![Tests](https://github.com/Wirg/stqdm/workflows/Tests/badge.svg)


## How to use

You can find some examples in `examples/`

### Use stqdm in main
```python
from time import sleep
from stqdm import stqdm

for _ in stqdm(range(50)):
    sleep(0.5)
```

### Use stqdm in sidebar
```python
from time import sleep
import streamlit as st
from stqdm import stqdm

for _ in stqdm(range(50), st_container=st.sidebar):
    sleep(0.5)
```
