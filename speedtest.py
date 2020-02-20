from surfacedetection.point import Point
import time

t = time.time()
h = [i for i in range(100000)]

for i in range(1000):
	h.remove(i)

print(time.time() - t)