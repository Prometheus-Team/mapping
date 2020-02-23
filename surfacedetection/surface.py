import numpy as np
import random

from balancer import HSVBalancer


class Surface:

	def __init__(self, surfaceSet):
		self.surfaceSet = surfaceSet
		self.adjacents = []
		self.balancer = HSVBalancer()
		self.mask = np.zeros(surfaceSet.picture.getShape(), dtype=np.int32)
		self.color = [random.randrange(255) for i in range(3)]

	def getExpandablePoints(self):
		shift = 1
		rshift = np.pad(self.mask, ((0,0),(shift,0)))[:,:-shift]
		lshift = np.pad(self.mask, ((0,0),(0,shift)))[:,shift:]
		
		hshift = np.maximum(np.maximum(rshift, lshift), self.mask)

		dshift = np.pad(hshift, ((shift, 0), (0, 0)))[:-shift,:]
		ushift = np.pad(hshift, ((0,shift),(0,0)))[shift:,:]

		tshift = np.maximum(np.maximum(dshift, ushift), hshift)

		return np.where(tshift - self.mask)

	def addRect(self, x, y, x1, y1):
		self.mask[y:y1, x:x1]

	def appendPoint(self, point):
		self.mask[point] = 1

	def getCoverage(self):
		return np.count_nonzero(self.mask)

	def contains(self, point):
		return self.mask[point] == 1

	def getColorAt(self, point):
		self.surfaceSet.picture.getColorAt(point)

	def getDepthAt(self, point):
		self.surfaceSet.picture.getDepthAt(point)

