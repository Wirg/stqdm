# stqdm
![Tests](https://github.com/Wirg/stqdm/workflows/Tests/badge.svg)
[![codecov](https://codecov.io/gh/Wirg/stqdm/branch/main/graph/badge.svg?token=YeHnzpfMty)](https://codecov.io/gh/Wirg/stqdm)
[![CodeQL](https://github.com/Wirg/stqdm/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/Wirg/stqdm/actions/workflows/codeql-analysis.yml)

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

### Display a progress bar during pandas Dataframe & Series operations
STqdm inherits from tqdm, you can call stqdm.pandas() in a similar way. See [tqdm docs](https://github.com/tqdm/tqdm#pandas-integration).
```python
from time import sleep

import pandas as pd
from stqdm import stqdm

stqdm.pandas()

pd.Series(range(50)).progress_map(lambda x: sleep(1))
pd.Dataframe({"a": range(50)}).progress_apply(lambda x: sleep(1), axis=1)
```

### Display the progress bar only in the frontend or the backend

```python
from time import sleep

from stqdm import stqdm

# Default to frontend only
for i in stqdm(range(50), backend=False, frontend=True):
    sleep(0.5)


for i in stqdm(range(50), backend=True, frontend=False):
    sleep(0.5)
```
