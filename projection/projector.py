
import numpy as np
from scipy import ndimage
import cv2 as cv
import math
from previewer import *
from numpy import genfromtxt
import pyrr
import matplotlib.pyplot as plt

from normalestimator import NormalEstimator

class Projector:

	def __init__(self):
		self.cloudset = None
		self.width, self.height = 640, 480
		self.dwidth, self.dheight = 320, 240
		self.dx, self.dy = 48, 27
		self.hfovd, self.vfovd = 57, 43
		self.slantThreshold = 4
		self.slantSeparation = 1e6
		self.separationThreshold = 1e3

		self.edgeImage = None
		self.edgeStrengthThreshold = 0.1

		self.xx, self.yy = None, None

	def openImage(self, rgb):
		self.rgb = rgb
		edges = cv.Canny(cv.cvtColor(rgb, cv.COLOR_BGR2GRAY), 50, 50)
		dst = np.clip(cv.blur(edges, (5,5)).astype(dtype=np.uint16) * 10, 0, 255)
		self.edgeImage = cv.resize(dst, (self.dx, self.dy), interpolation = cv.INTER_AREA).astype(np.float32)/255
		# plt.imshow(self.edgeImage, cmap='gray')
		# plt.show()

	def openDepth(self, depth):
		self.depth = cv.resize(depth, (self.dx, self.dy), interpolation = cv.INTER_AREA)
		self.worldCoords(self.dx, self.dy)

	def projectDepth(self, cameraTransform):
		points = self.getProjectedPoints(cameraTransform)
		edgePoints = self.getEdgePoints(points.copy())
		normals = NormalEstimator.getEstimatedNormals(points)
		points, normals = self.clean(points, normals)
		return points, normals, edgePoints

	def getEdgePoints(self, points):
		# print(points.shape)
		# print(self.edgeImage[...,np.newaxis].shape)
		edgePoints = np.concatenate((points, self.edgeImage[...,np.newaxis]), axis=-1)
		# print(edgePoints.shape)
		edgePoints = edgePoints[edgePoints[...,3] > self.edgeStrengthThreshold]
		# print(edgePoints.shape)
		return edgePoints


	def edges(self, d):
		dx = ndimage.sobel(d, 0)
		dy = ndimage.sobel(d, 1)
		return np.abs(dx) + np.abs(dy)

	def worldCoords(self, width, height):
		hFov = math.radians(self.hfovd)
		vFov = math.radians(self.vfovd)
		cx, cy = width/2, height/2
		fx = width/(2*math.tan(hFov/2))
		fy = height/(2*math.tan(vFov/2))
		xx, yy = np.tile(range(width), height), np.repeat(range(height), width)
		xx = ((xx + 0.5)-cx)/fx
		yy = ((yy + 0.5)-cy)/fy
		self.xx, self.yy = xx, yy

	def getProjectedPoints(self, cameraTransform):
		points = self.posFromDepth(self.depth.copy())
		points = rotate(points, (0,-90,180))
		points = transform(points, cameraTransform)
		return points.astype(dtype = np.float32).reshape((self.dy, self.dx, 3))

	def posFromDepth(self, depth):
		length = depth.shape[0] * depth.shape[1]

		depth[self.edges(depth) > self.slantThreshold] = self.slantSeparation
		z = depth.reshape(length);

		return np.dstack((self.xx * z, self.yy * z, z)).reshape((length, 3))

	def clean(self, points, normals):
		points[np.abs(points) > self.separationThreshold] = np.nan
		points = points.reshape((-1,3))
		normals = normals.reshape((-1,3))

		condition = np.logical_not(np.any(np.isnan(points), axis=1))
		points = points[condition]
		normals = normals[condition]

		return points, normals


	def getBounds(self, points, bubbleResolution):
		#extent = bubbleResolution//2
		points[np.abs(points) > self.separationThreshold] = np.nan
		maxBound = np.nanmax(np.nanmax(points, axis = 1), axis = 0)
		minBound = np.nanmin(np.nanmin(points, axis = 1), axis = 0)# - extent
		return (minBound, maxBound)


if __name__ == '__main__':
	depth = genfromtxt('../testdata/depth3.csv', delimiter=',') * 10
	img = cv.imread('../testdata/ClippedDepthNormal.png')
	cameraTransform = matrixTR((1,2,0),(0,50,40))

	p = Projector()
	p.openImage(img)
	p.openDepth(depth)
	points, normals, edgePoints = p.projectDepth(cameraTransform)

	print(p.getBounds(points, 7))

	m = ModelPreview()
	m.start()

	colors = np.ones(points.shape)
	colors[np.all(normals == 0, axis=1)] = (1,0.5,0)

	normalProjections = points + normals/10
	normalDraw = np.concatenate((points, normalProjections), axis=1)

	m.addRenderable(Renderable(edgePoints[:,0:3], Renderable.POINTS, color=(0.1, 0.6,1)))
	# m.addRenderable(Renderable(points, Renderable.POINTS, pointSize=3, color=colors))
	# m.addRenderable(Renderable(normalDraw, Renderable.WIREFRAME, color=(0.1, 0.6,1)))
	m.addCamera(Camera(57, 43, cameraTransform))

