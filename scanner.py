import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

v = [[[1, 0, 0, 1.0] for i in range(10)] for i in range(10)]
vn = np.array(v)
implt = plt.imshow(vn)

# put a blue dot at (10, 20)
plt.scatter([10], [20])

# put a red dot, size 40, at 2 locations:
plt.scatter(x=[30, 40,50, 60], y= [30, 40,50, 60], c='r', s=40)

plt.show()