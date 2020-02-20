import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

b=np.array([0,0,0.5, 1.0])
b=b.reshape(1,4)
b=np.repeat(b,240, axis=0)
b=b.reshape(1,240,4)
b=np.repeat(b, 320, axis=0)
print(b.shape)

it = np.nditer(b, flags=['multi_index'])
while not it.finished:
	print("%d <%s>" % (it[0], it.multi_index), end=' ')
	it.iternext()

implt = plt.imshow(b)
plt.show()