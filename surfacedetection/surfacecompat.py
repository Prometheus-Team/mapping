from util import *
from balancer import HSVBalancer
from point import Point
import numpy as np
import random


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
				out += " " + str(self.strips[i]) + "\n"
		return out



	def getExpandablePoints(self):
		expandablePoints = []
		for i in self.strips:
			for j in self.strips[i].getExpandablePoints(i):
				if j not in expandablePoints:
					expandablePoints.append(j)

				etcnt('bttl')

		return expandablePoints

	def getMultiExpandablePoints(self):
		expandablePoints = np.zeros(self.surfaceSet.picture.getShape())
		for i in self.strips:
			btcnt('bttl')
			indices = np.array(self.strips[i].getExpandablePoints(i), dtype=np.int64).transpose()
			print(indices)
			expandablePoints[indices] = 1
			etcnt('bttl')
		#print("Expandable Points:", len(expandablePoints))

		# for i in expandablePoints:
		# 	container = self.surfaceSet.getSurfaceContaining(i)
		# 	if container not in self.adjacents:
		# 		self.adjacents.append(i)
		print(np.array(np.where(expandablePoints == 1)))
		return np.array(np.where(expandablePoints == 1)).transpose()

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

	def getExpandablePoints(self, stripNumber = -1):

		if len(self.edges) == 0:
			return []

		#print("Has edges")

		onPreviousStrip = []
		onCurrentStrip = []
		onNextStrip = []

		previousStrip, nextStrip, stripNumber = self.getAdjacentStrips(stripNumber)
		previousStripNumber = stripNumber - 1
		nextStripNumber = stripNumber + 1
		width = self.surface.surfaceSet.picture.getWidth()		
		# # print("Width is", width)

		# for i in self.edges:
		# 	horizontals = i.getHorizontallySurroundingPixels()
		# 	verticals = i.getVerticallySurroundingPixels()
		# 	onCurrentStrip = [(i, stripNumber) for i in horizontals if i < width]
		# 	for j in verticals:
		# 		if previousStrip:
		# 			if not previousStrip.contains(j) and j < width:
		# 				onPreviousStrip.append((j, previousStripNumber))
		# 		if nextStrip:
		# 			if not nextStrip.contains(j) and j < width:
		# 				onNextStrip.append((j, nextStripNumber))

		# print("Iterative:",onCurrentStrip + onPreviousStrip + onNextStrip)



		onPreviousStrip = []
		onCurrentStrip = []
		onNextStrip = []
		pairs = []
		
		for i in self.edges:
			pixelRange = i.getHorizontallySurroundingPixels()
			pairs.append(pixelRange)
			onCurrentStrip = [(i, stripNumber) for i in pixelRange if i < width]

		previousRange = []
		nextRange = []


		if previousStrip:		
			# print("Subtract:",previousStrip.getPairs(),"from",pairs)
			previousRange = SurfaceStrip.Subtract(pairs, previousStrip.getPairs())
		if nextStrip:
			# print("Subtract:",nextStrip.getPairs(),"from",pairs)
			nextRange = SurfaceStrip.Subtract(pairs, nextStrip.getPairs())
			# print("Output:", nextRange)
		
		for i in previousRange:
			onPreviousStrip += [(j, previousStripNumber) for j in range(i[0], i[1] + 1) if j < width]
		for i in nextRange:
			onNextStrip += [(j, nextStripNumber) for j in range(i[0], i[1] + 1) if j < width]


		# print("Subtract:",onCurrentStrip + onPreviousStrip + onNextStrip)

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

	def getAdjacentStrips(self, stripNumber = -1):

		if stripNumber == -1:
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

	def getPairs(self):
		return [(i.left, i.right) for i in self.edges]

	def addEdgePair(self, edgePair):
		self.edges.append(edgePair)
		# cnt('addEdge')
		self.edges.sort(key = lambda x: x.left)
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

	def Subtract(fromPairs, pairs):

		if (len(pairs) == 0):
			return fromPairs

		if (len(fromPairs) == 0):
			return []

		FROMSTART = 2
		START = 1
		FROMEND = -2
		END = -1

		seq = [(i[1], FROMSTART) for i in fromPairs]
		seq += [(i[1], START) for i in pairs]
		seq += [(i[0], FROMEND) for i in fromPairs]
		seq += [(i[0], END) for i in pairs]
		seq.sort(key = lambda x: x[0], reverse = True)

		#print(seq)

		difference = []

		lkey = None
		lstatus = 0
		status = 0

		for i in seq:
			status += i[1]
			if (lstatus == 2 and status != 1) and lkey != i[0]:
				difference.append((i[0] + 1, lkey - 1))
			lstatus = status
			lkey = i[0]

		difference.reverse()

		if len(difference) > 0:
			difference[0] = (difference[0][0] - 1, difference[0][1])
			difference[-1] = (difference[-1][0], difference[-1][1] + 1)

		return difference


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
		return (i for i in range(self.left - 1, self.right + 2))

	def getVerticallySurroundingPixelRanges(self):
		return (self.left - 1, self.right + 1)

	def getHorizontallySurroundingPixels(self):
		return (self.left - 1, self.right + 1)

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


# e = [(2,3),(5,6)]
# f = [(1,7)]

# print(SurfaceStrip.Subtract(f,e))