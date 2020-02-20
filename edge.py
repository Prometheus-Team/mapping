import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import time

t = time.time()

img = cv.imread('testdata/ClippedDepthNormal.png',0)
edges = cv.Canny(img,50,50)

dst = cv.blur(edges, (20,20))
dst = cv.blur(dst, (30,30))
dst = cv.blur(dst, (50,50))

print(time.time() - t)



plt.subplot(131),plt.imshow(img,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(132),plt.imshow(edges,cmap = 'gray')
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
plt.subplot(133),plt.imshow(dst, cmap = 'gray')
plt.title('Averaging'), plt.xticks([]), plt.yticks([])
plt.show()