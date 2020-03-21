import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import time
import random
import cv2 as cv


def diff(x1, x2):
	xout = x2 - x1
	xout[3] = 1.0
	return xout

def pair(img1, img2):
	return np.concatenate((img1, img2), 1)

img = cv.imread('testdata/ClippedDepthNormal.png')
rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
print(rgb.shape)
dx = np.ndarray(img.shape)

t = time.time()

edges = cv.Canny(img,50,50)

dst = cv.blur(edges, (20,20))
dst = cv.blur(dst, (30,30))
dst = cv.blur(dst, (50,50))

scamnt = 1000
sc = [[random.randrange(0, img.shape[1]) for i in range(scamnt)], [random.randrange(0, img.shape[0]) for i in range(scamnt)]]
sizes = []

sc2 = [[],[]]

for i in range(len(sc[0])):
	chance = dst[sc[1][i]][sc[0][i]]/255
	if (random.random() < (chance**2)*5):
		sc2[0].append(sc[0][i])
		sc2[1].append(sc[1][i])
		sizes.append(5)

print(time.time() - t)

implt = plt.imshow(edges)
#implt = plt.imshow(dst)


#plt.scatter(x=sc2[0], y=sc2[1], c='r', s=sizes)

plt.show()