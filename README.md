# stqdm
![Tests](https://github.com/Wirg/stqdm/workflows/Tests/badge.svg)
[![codecov](https://codecov.io/gh/Wirg/stqdm/branch/main/graph/badge.svg?token=YeHnzpfMty)](https://codecov.io/gh/Wirg/stqdm)

stqdm is the simplest way to handle a progress bar in streamlit app.

![demo gif](https://raw.githubusercontent.com/Wirg/stqdm/main/assets/demo.gif)

## How to install

```sh
pip install stqdm
```

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

### Customize the bar with tqdm parameters

![demo gif](https://raw.githubusercontent.com/Wirg/stqdm/main/assets/demo_with_custom_params.gif)

```python
from time import sleep
from stqdm import stqdm

for _ in stqdm(range(50), desc="This is a slow task", mininterval=1):
    sleep(0.5)
```
