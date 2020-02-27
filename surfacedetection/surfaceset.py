import numpy as np
from surface import Surface

class SurfaceSet:

	def __init__(self):
		self.surfaces = []
		self.picture = None

	def addSurface(self, surface):
		self.surfaces.append(surface)
		surface.surfaceSet = self

	def removeSurface(self, surface):
		self.surfaces.remove(surface)

	def isContained(self, point):
		return self.getSurfaceContaining(point) != None

	def getSurfaceContaining(self, point):
		for i in self.surfaces:
			if i.contains(point):
				return i

	def getTotalCoverage(self):
		coverage = 0
		for i in self.surfaces:
			coverage += i.getCoverage()
		return coverage

	def createSurface(self):
		surface = Surface(self)
		self.surfaces.append(surface)
		return surface

	def checkForOverlaps(self):
		maskSum = np.zeros(self.picture.getShape())
		for i in self.surfaces:
			maskSum += i.mask
		maskSum = np.clip(maskSum - 1, 0, 1)
		return np.count_nonzero(maskSum) > 0, maskSum 