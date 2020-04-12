from surfacedetection.point import Point
import time

t = time.time()
h = []

for i in range(10000):
	if (i,i) not in h:
		h.append((i,i))

print(time.time() - t)







