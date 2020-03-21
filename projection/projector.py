
import numpy as np
from scipy import ndimage
import cv2 as cv
import math
from previewer import ModelPreview
from numpy import genfromtxt


# Image shapes
height_rgb, width_rgb = 480, 640
height_depth, width_depth = height_rgb // 2, width_rgb // 2
rgb_width = width_rgb
rgb_height = height_rgb

# Compute edge magnitudes
def edges(d):
	dx = ndimage.sobel(d, 0)  # horizontal derivative
	dy = ndimage.sobel(d, 1)  # vertical derivative
	return np.abs(dx) + np.abs(dy)

class Projector:

	def __init__(self):
		self.rgb = []
		self.depth = []

	def openImage(self, rgb):
		self.rgb = rgb

	def openDepth(self, depth):
		self.depth = depth

	def worldCoords(self, width, height):
		hfov_degrees, vfov_degrees = 57, 43
		hFov = math.radians(hfov_degrees)
		vFov = math.radians(vfov_degrees)
		cx, cy = width/2, height/2
		fx = width/(2*math.tan(hFov/2))
		fy = height/(2*math.tan(vFov/2))
		xx, yy = np.tile(range(width), height), np.repeat(range(height), width)
		xx = (xx-cx)/fx
		yy = (yy-cy)/fy
		return xx, yy

	def posFromDepth(self, depth, xx, yy):
		length = depth.shape[0] * depth.shape[1]

		#depth[edges(depth) > 0.3] = 1e6  # Hide depth edges       
		z = depth.reshape(length)

		return np.dstack((xx*z, yy*z, z)).reshape((length, 3))

	def getDepth(self):
		xx, yy = self.worldCoords(width=rgb_width//2, height=rgb_height//2)
		points = self.posFromDepth(self.depth.copy(), xx, yy)
		return points


img = cv.imread('../testdata/ClippedDepthNormal.png')
img = cv.resize(img, (640, 480), interpolation = cv.INTER_AREA)
rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
img = cv.imread('../testdata/ClippedDepthZ.png')
img = cv.resize(img, (320, 240), interpolation = cv.INTER_AREA)
depth = cv.cvtColor(img, cv.COLOR_BGR2RGB)[:,:,0]
depth = depth.astype(dtype=np.float32)/25555

depth = genfromtxt('../testdata/depth2.csv', delimiter=',')

print("Depth")
print(depth)
p = Projector()
p.openDepth(depth)
points = p.getDepth().astype(dtype=np.float32)
print(points.shape)
print(points[90:100])
m = ModelPreview()
m.start()
m.ShowPoints(points, pointSize=5)
