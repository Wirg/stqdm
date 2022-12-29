from time import sleep

from stqdm import stqdm

LENGTH = 50
INCREMENT = 1

progress = stqdm(total=LENGTH)
INDEX = 0
while True:
    INDEX += INCREMENT
    if INDEX == LENGTH:
        break
    progress.update(INCREMENT)
    sleep(0.5)
