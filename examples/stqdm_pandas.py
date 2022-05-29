from time import sleep

import pandas as pd
from stqdm import stqdm

stqdm.pandas()

pd.Series(range(50)).progress_map(lambda x: sleep(1))
