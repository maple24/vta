import queue
import time

q = queue.Queue()

for i in range(1000):
    q.put((time.time(), "first"))
    q.put((time.time(), "second"))

# print(list(q.queue[1]))

print([x[1] for x in q.queue])

from datetime import datetime

print(datetime.now().replace(microsecond=0))
import os

print(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3]))
