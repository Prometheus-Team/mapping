import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import time

t = time.time()

# img = cv.imread('testdata/ClippedDepthNormal.png',0)
img = cv.imread('testdata/ClippedDepthNormal.png')
img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
# img = np.clip((np.genfromtxt('testdata/depth3.csv', delimiter=',') * 500), 0, 255).astype(dtype=np.uint8)
edges = cv.Canny(img, 60, 60)

l1 = 10
l2 = 20
l3 = 0

dst = np.clip(cv.blur(edges, (l1,l1)).astype(dtype=np.uint16) * 15, 0, 255)

print(dst.shape)
print(dst)

dst = cv.blur(dst, (l2,l2))
# dst = cv.blur(dst, (l3,l3))

print(time.time() - t)

plt.subplot(131),plt.imshow(img,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(132),plt.imshow(edges,cmap = 'gray')
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
plt.subplot(133),plt.imshow(dst, cmap = 'gray')
plt.title('Averaging'), plt.xticks([]), plt.yticks([])
plt.show()