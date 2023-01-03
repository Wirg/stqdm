"""
Example with generator.
See : https://github.com/Wirg/stqdm/issues/16#issuecomment-1078823696
"""

from time import sleep

from stqdm import stqdm

values = ["a", "b", "c"]
for count, value in enumerate(stqdm(values)):
    sleep(1)
