
from surface import Surface

class SurfaceSet:

	def __init__(self):
		self.surfaces = []
		self.picture = None

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