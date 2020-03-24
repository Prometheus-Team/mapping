
import numpy as np
from scipy import ndimage
import cv2 as cv
import math
from previewer import *
from numpy import genfromtxt
import pyrr

class Projector:

	def __init__(self):
		self.cloudset = None
		self.width, self.height = 640, 480
		self.dwidth, self.dheight = 320, 240
		self.dx, self.dy = 35, 20
		self.hfovd, self.vfovd = 57, 43
		self.slantThreshold = 4

	def openImage(self, rgb):
		self.rgb = rgb

	def openDepth(self, depth):
		self.depth = cv.resize(depth, (self.dx, self.dy), interpolation = cv.INTER_AREA)

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
		xx = (xx-cx)/fx
		yy = (yy-cy)/fy
		return xx, yy

	def posFromDepth(self, depth, xx, yy):
		length = depth.shape[0] * depth.shape[1]

		#depth[self.edges(depth) > 0.99] = 1e6  # Hide depth edges  
		depth[self.edges(depth) > self.slantThreshold] = 1e6
		z = depth.reshape(length)

		return np.dstack((xx*z, yy*z, z)).reshape((length, 3))

	def getEstimatedNormals(self, points):
		infinitum = (1e6, 1e6, 1e6)
		infinitumThreshold = 1e3

		#shift points right, left, down, up
		rollr = np.roll(points, 1, axis=1)
		rollr[:,0] = infinitum

		rolll = np.roll(points, -1, axis=1)
		rolll[:,-1] = infinitum

		rolld = np.roll(points, 1, axis=0)
		rolld[0,:] = infinitum

		rollu = np.roll(points, -1, axis=0)
		rollu[-1,:] = infinitum

		#find the differences
		diffr = rollr - points
		diffl = rolll - points
		diffu = rollu - points
		diffd = rolld - points

		#cross product differences to find normals
		crossrd = np.cross(diffr, diffd)
		crosslu = np.cross(diffl, diffu)

		#average the two normals
		normals = normalize(crosslu + crossrd)

		#set border normals to zero
		normals[np.sum((np.abs(diffr), np.abs(diffl), np.abs(diffu), np.abs(diffd)), axis=0) > infinitumThreshold] = 0


		return normals


	def getProjectedPoints(self):
		xx, yy = self.worldCoords(self.dx, self.dy)
		points = self.posFromDepth(self.depth.copy(), xx, yy)
		points = transform(points, pyrr.Matrix44.from_x_rotation(np.pi))
		return points.astype(dtype = np.float32).reshape((self.dy, self.dx, 3))







if __name__ == '__main__':
	depth = genfromtxt('../testdata/depth2.csv', delimiter=',')

	p = Projector()
	p.openDepth(depth)
	points = p.getProjectedPoints()
	normals = p.getEstimatedNormals(points)

	print(points)
	m = ModelPreview()
	m.start()

	colors = np.ones(points.shape)
	colors[np.all(normals == 0, axis=2)] = (1,0.5,0)
	print(colors.shape)

	normalProjections = points + normals/10
	normalDraw = np.concatenate((points, normalProjections), axis=2)

	m.addRenderable(Renderable(points, Renderable.POINTS, pointSize=3, color=colors))
	m.addRenderable(Renderable(normalDraw, Renderable.WIREFRAME, color=(0.1, 0.6,1)))