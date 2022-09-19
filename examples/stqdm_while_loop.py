from time import sleep

from stqdm import stqdm

length = 50
increment = 1

progress = stqdm(total=length)
index = 0
while True:
    index += increment
    if index == length:
        break
    progress.update(increment)
    sleep(0.5)
