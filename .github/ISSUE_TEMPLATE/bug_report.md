---
name: Bug report
about: Report a bug
title: "[BUG]"
labels: bug
assignees: ''

---

**Describe the bug**

A clear and concise description of what the bug is.

**To Reproduce**

Steps to reproduce the behavior and snippet
Example :

```python
from time import sleep

import pandas as pd
from stqdm import stqdm

stqdm.pandas()

pd.Series(range(50)).progress_map(lambda x: sleep(1))
```

**Expected behavior**

A clear and concise description of what you expected to happen.

**Screenshots**

If applicable, add screenshots to help explain your problem.

**Desktop (please complete the following information):**

 - OS: [e.g. Ubuntu 18.0.4]
 - Browser [e.g. chrome, safari]
 - Version of streamlit [e.g.  0.83.0]
 - Version of stqdm [e.g. 0.0.4]
 - Version of tqdm [e.g. 4.61.1]

**Additional context**

Add any other context about the problem here.
