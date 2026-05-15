# stqdm
![Tests](https://github.com/Wirg/stqdm/workflows/Tests/badge.svg)
[![codecov](https://codecov.io/gh/Wirg/stqdm/branch/main/graph/badge.svg?token=YeHnzpfMty)](https://codecov.io/gh/Wirg/stqdm)
[![CodeQL](https://github.com/Wirg/stqdm/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/Wirg/stqdm/actions/workflows/codeql-analysis.yml)
[![Downloads](https://static.pepy.tech/personalized-badge/stqdm?period=month&units=international_system&left_color=grey&right_color=brightgreen&left_text=downloads/month)](https://pepy.tech/project/stqdm)
![Supported Python Versions](https://img.shields.io/pypi/pyversions/stqdm)
![pypi version](https://img.shields.io/pypi/v/stqdm)

stqdm is the simplest way to handle a progress bar in streamlit app.

![demo gif](https://raw.githubusercontent.com/Wirg/stqdm/main/assets/demo.gif)

## How to install

```sh
pip install stqdm
```

## Development

This project uses `uv` for packaging and dependency management, with `mise` managing local tools and sourcing uv's `.venv`.
Trust the local mise config once, then install tools and dependencies:

```sh
mise trust
mise install
mise run install
mise run test
```

`mise` manages local tools, `uv` manages the project environment and lockfile, and `nox` creates isolated compatibility environments. Nox is configured to use uv as its virtualenv backend when available.

Compatibility checks are managed with `nox`:

```sh
mise run nox-list
mise run compat
```

## How to use

You can find runnable examples in `examples/` and the Streamlit demo app in `demo/`.

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

### Setting Default Configuration
stqdm can set default configuration for all future progress bars.

```python
from time import sleep

from stqdm import stqdm

# Set default configuration to suppress frontend display
stqdm.set_default_config(frontend=False)

# Utilize stqdm with the default configuration
# It will use the new default configuration with frontend=False
for _ in stqdm(range(50)):
    sleep(0.5)
```

### Scoped Configuration
Use `scope` to temporarily override default arguments in a `with` block.

```python
from time import sleep

import streamlit as st
from stqdm import stqdm

# Override default settings temporarily within a scope
with stqdm.scope(desc="Processing", bar_format="{desc}"):
    for _ in stqdm(range(10)):
        sleep(0.5)

# Outside the scope, stqdm reverts to the default settings
for _ in stqdm(range(10)):
    sleep(0.5)

# Attach all the stqdm instances used inside the scope
# to the sidebar, then go back to normal
with stqdm.scope(st_container=st.sidebar):
    function_1()
    function_2()
```

### Going further with configuration management

See `examples/stqdm_scopes.py` for a complete scoped configuration example.
