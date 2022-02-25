# multi_threaded.py
import time
from concurrent.futures import *

COUNT = 500000000


def countdown(n):
    while n > 0:
        n -= 1


start = time.time()
with ThreadPoolExecutor(max_workers=4) as e:
    e.submit(countdown, COUNT // 2)
    e.submit(countdown, COUNT // 2)
end = time.time()

print('Time taken in seconds -', end - start)
