from time import sleep

from stqdm import stqdm

LENGTH = 50
INCREMENT = 1

progress = stqdm(total=LENGTH)
index = 0
while True:
    index += INCREMENT
    if index == LENGTH:
        break
    progress.update(INCREMENT)
    sleep(0.5)
