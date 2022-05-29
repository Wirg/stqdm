from time import sleep

from stqdm import stqdm

for _ in stqdm(range(50)):
    progress_bar = stqdm(range(15))
    for _ in progress_bar:
        sleep(0.5)
    progress_bar.st_clear()
