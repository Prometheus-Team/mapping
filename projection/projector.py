
import numpy as np
from scipy import ndimage
import cv2 as cv
import math
from previewer import *
from numpy import genfromtxt
import pyrr


# Image shapes
height_rgb, width_rgb = 480, 640
height_depth, width_depth = height_rgb // 2, width_rgb // 2
rgb_width = width_rgb
rgb_height = height_rgb

dx, dy = 96, 54


class Projector:

	def __init__(self):
		self.cloudset = None

	def openImage(self, rgb):
		self.rgb = rgb

	def openDepth(self, depth):
		self.depth = depth

	def edges(self, d):
		dx = ndimage.sobel(d, 0)
		dy = ndimage.sobel(d, 1)
		return np.abs(dx) + np.abs(dy)

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

		depth[self.edges(depth) > 0.9] = 1e6  # Hide depth edges       
		z = depth.reshape(length)

		return np.dstack((xx*z, yy*z, z)).reshape((length, 3))

	def getProjectedPoints(self):
		xx, yy = self.worldCoords(width = dx, height = dy)
		points = self.posFromDepth(self.depth.copy(), xx, yy)
		points = np.append(points, np.ones((points.shape[0], 1)), axis=1).dot(pyrr.Matrix44.from_x_rotation(np.pi))
		return points[:,0:3].astype(dtype = np.float32)



if __name__ == '__main__':
	depth = genfromtxt('../testdata/depth3.csv', delimiter=',') * 10
	depth = cv.resize(depth, (dx, dy), interpolation = cv.INTER_AREA)

	p = Projector()
	p.openDepth(depth)

	points = p.getProjectedPoints()

	print(points)
	m = ModelPreview()
	m.start()
	m.addRenderable(Renderable(points, Renderable.POINTS, pointSize=1))
