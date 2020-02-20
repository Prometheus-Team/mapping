from util import *
from balancer import HSVBalancer
from point import Point
import random

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


class Surface:

	def __init__(self, surfaceSet):
		self.surfaceSet = surfaceSet
		self.adjacents = []
		self.balancer = HSVBalancer()
		self.strips = {i:SurfaceStrip(self) for i in range(self.surfaceSet.picture.getHeight())}
		self.color = [random.randrange(255) for i in range(3)]

	def __str__(self):
		out = ""
		for i in self.strips:
			if len(self.strips[i].edges) > 0:
				out += " " + str(self.strips[i])
		return out

	def getExpandablePoints(self):
		expandablePoints = []
		for i in self.strips:
			cnt('expandablePoints')
			for j in self.strips[i].getExpandablePoints():
				if j not in expandablePoints:
					expandablePoints.append(j)

		#print("Expandable Points:", len(expandablePoints))

		# for i in expandablePoints:
		# 	container = self.surfaceSet.getSurfaceContaining(i)
		# 	if container not in self.adjacents:
		# 		self.adjacents.append(i)

		return expandablePoints

	def addRect(self, x, y, x1, y1):
		for i in range(y, y1):
			self.strips[i].cover(x, x1)

	def appendPoint(self, point):
		#print("Appending", point)
		self.strips[point[1]].append(point[0])

	def getCoverage(self):
		coverage = 0
		for i in self.strips:
			coverage += self.strips[i].getCoverage()
		return coverage

	def contains(self, point):
		strip = self.strips[point[1]]
		return strip.contains(point[0])

	def getColorAt(self, point):
		self.surfaceSet.picture.getColorAt(point)

	def getDepthAt(self, point):
		self.surfaceSet.picture.getDepthAt(point)


	#statics

	def Merge(surface1, surface2):
		nsurface = Surface()

		set1 = set(surface1.strips.keys())
		set2 = set(surface2.strips.keys())

		for i in set1.difference(set2):
			nsurface.strips[i] = surface1.strips[i]

		for i in set2.difference(set2):
			nsurface.strips[i] = surface2.strips[i]

		for i in set1.intersect(set2):
			nstrip = SurfaceStrip.Merge(surface1.strips[i], surface2.strip2[i])

		return nsurface

		

class SurfaceStrip:

	def __init__(self, surface):
		self.surface = surface
		self.edges = []

	def __str__(self):
		out = ""
		for i in self.edges:
			out += " " + str(i)
		return out

	def getExpandablePoints(self):

		if len(self.edges) == 0:
			return []

		#print("Has edges")

		onPreviousStrip = []
		onCurrentStrip = []
		onNextStrip = []

		previousStrip, nextStrip, stripNumber = self.getAdjacentStrips()

		for i in self.edges:
			onCurrentStrip.extend(i.getHorizontallySurroundingPixels())
			if previousStrip:
				onPreviousStrip.extend(i.getVerticallySurroundingPixels())
			if previousStrip and nextStrip:
				onNextStrip = onPreviousStrip.copy()
			elif nextStrip:
				onNextStrip.extend(i.getVerticallySurroundingPixels())


		if previousStrip:
			for i in onPreviousStrip:
				if previousStrip.contains(i):
					onPreviousStrip.remove(i)
			previousStripNumber = previousStrip.getStripNumber()
			onPreviousStrip = [(i, previousStripNumber) for i in onPreviousStrip]
		
		currentStripNumber = self.getStripNumber()
		onCurrentStrip = [(i, currentStripNumber) for i in onCurrentStrip]

		if nextStrip:
			for i in onNextStrip:
				if nextStrip.contains(i):
					onNextStrip.remove(i)
			nextStripNumber = nextStrip.getStripNumber()
			onNextStrip = [(i, nextStripNumber) for i in onNextStrip]

		# print("Previous Strip:", [str(i) for i in onPreviousStrip])
		# print("Current Strip:", [str(i) for i in onCurrentStrip])
		# print("Next Strip:", [str(i) for i in onNextStrip])

		return onCurrentStrip + onPreviousStrip + onNextStrip

	def append(self, pointx):

		#print("Was:", self)

		added = False
		for i in self.edges:
			if i.isAdjacent(pointx):
				i.append(pointx)
				added = True
		
		if not added:
			self.addEdgePair(EdgePair(pointx, pointx))

		#print("Is:", self)

	def cover(self, x, x1):
		self.addEdgePair(EdgePair(x, x1))

	def getPreviousStrip(self):
		stripNumber = self.getStripNumber()
		if stripNumber - 1 in self.surface.strips:
			return self.surface.strips[stripNumber - 1]

	def getNextStrip(self):
		stripNumber = self.getStripNumber()
		if stripNumber + 1 in self.surface.strips:
			return self.surface.strips[stripNumber + 1]

	def getAdjacentStrips(self):
		stripNumber = self.getStripNumber()
		previousStrip = None
		nextStrip = None
		if stripNumber - 1 in self.surface.strips:
			previousStrip = self.surface.strips[stripNumber - 1]
		if stripNumber + 1 in self.surface.strips:
			nextStrip = self.surface.strips[stripNumber + 1]
		return previousStrip, nextStrip, stripNumber

	def getStripNumber(self):
		for i in self.surface.strips:
			if self.surface.strips[i] == self:
				return i

	def addEdgePair(self, edgePair):
		self.edges.append(edgePair)
		#print("Added Edge Pair:", edgePair)

	def contains(self, pointx):
		for i in self.edges:
			if Between(pointx, i.left, i.right):
				return True
		return False

	def getCoverage(self):
		coverage = 0
		for i in self.edges:
			coverage += (i[1] - i[0]) + 1
		return coverage

	#statics

	def Merge(strip1, strip2):
		nstrip = SurfaceStrip()
		merged = []

		pairs = strip1.edges + strip2.edges
		nstrip.edges = EdgePair.MergeOverlapping()
		return nstrip


class EdgePair:

	def Make(array):
		return EdgePair(array[0], array[1])

	def __init__(self, left, right):
		self.left = left
		self.right = right

	def __str__(self):
		return str((self.left, self.right))

	def isAdjacent(self, pointx):
		return pointx == self.left - 1 or pointx == self.right + 1

	def append(self, pointx):
		if pointx == self.left - 1:
			self.left = pointx
		elif pointx == self.right + 1:
			self.right = pointx

	def getVerticallySurroundingPixels(self):
		return [i for i in range(self.left - 1, self.right + 2)]

	def getHorizontallySurroundingPixels(self):
		return [self.left - 1, self.right + 1]

	#statics

	def MergeOverlapping(pairs):

		if len(pairs) == 0:
			return []

		pairs = sorted(pairs, key=lambda x: x.left)
		merged = [pairs[0]]

		for i in pairs:
			for j in merged:
				if EdgePair.Overlap(i, j):
					merged.remove(j)
					merged.append(EdgePair.Merge(i,j))
				else:
					merged.append(i)

		return merged


	def Overlap(pair1, pair2):
		return Between(pair1.left, pair2.left, pair2.right) or Between(pair2.left, pair1.left, pair1.right)

	def Merge(pair1, pair2):
		return EdgePair(min(pair1.left, pair2.left), max(pair1.right, pair2.right))
