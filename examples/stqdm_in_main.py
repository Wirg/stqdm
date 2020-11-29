from time import sleep

from stqdm import stqdm

for _ in stqdm(range(50)):
    sleep(0.5)
