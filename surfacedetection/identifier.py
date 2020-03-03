import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import time
import random
import cv2 as cv
import multiprocessing as mp

from surface import Surface
from surfaceset import SurfaceSet
from picture import *
from pointgeneration import *
import values
from explorer import *

class SurfaceIdentifier:

	def __init__(self):
		self.picture = None
		self.explorers = []
		self.surfaceSet = SurfaceSet()

	def setPicture(self, picture):
		self.picture = picture
		self.surfaceSet.picture = picture

	def identify(self):
		self.plantExplorers()
		self.startExploration()

	def plantExplorers(self):
		points  = self.generateExplorationPoints()
		# print(points)
		for i in points:
		# for i in [(10, 30),(30,30),(30,60)]:
			if not self.surfaceSet.isContained(i):
				explorer = Explorer(i, self.surfaceSet)
				explorer.declareSurface()
				self.explorers.append(explorer)


	def startExploration(self):
		print("exploring")

		# result = [pool.apply(Explorer.explore, args=(i, 4, 8)) for i in self.explorers]
		for i in range(values.identifier.expansionLimit):
			for j in self.explorers:
				j.explore()
			btcnt('merge')
			self.mergeOverlaps()
			etcnt('merge')
			# self.preview()  

	def mergeOverlaps(self):
		hasOverlaps, overlapMask = self.surfaceSet.checkForOverlaps()
		while hasOverlaps:
			self.mergeOverlapping(overlapMask)
			hasOverlaps, overlapMask = self.surfaceSet.checkForOverlaps()

	def mergeOverlapping(self, overlapMask):
		mergeIndex = np.where(overlapMask > 0)
		# print(mergeIndex)
		mergePoint = (mergeIndex[0][0], mergeIndex[1][0])
		mergables = []
		for i in self.surfaceSet.surfaces:
			if i.contains(mergePoint):
				mergables.append(i)
		# print("Merging",mergables[0].color,"and",mergables[1].color)
		nSurface = Surface.Merge(mergables)
		self.surfaceSet.addSurface(nSurface)
		for i in mergables:
			self.surfaceSet.removeSurface(i)

		lExplorer = None
		for i in tuple(self.explorers):
			if i.surface in mergables:
				self.explorers.remove(i)
				lExplorer = i
		self.explorers.append(lExplorer)
		lExplorer.surface = nSurface
		lExplorer.reset()

	def isExplorationComplete(self):
		totalArea = self.picture.getWidth() * self.picture.getHeight()
		exploredArea = self.surfaceSet.getTotalCoverage()
		return exploredArea/totalArea > values.identifier.explorationThreshold
		
	def preview(self):
		print(len(self.surfaceSet.surfaces))
		print(len(self.explorers))

		img = np.copy(self.picture.rgb)

		for i in self.surfaceSet.surfaces:
			d = 3
			color = np.tile(i.color, self.picture.getShape()).reshape(self.picture.getShape()[0], self.picture.getShape()[1], d)
			mask = np.repeat(i.mask, d).reshape(self.picture.getShape()[0], self.picture.getShape()[1], d)
			mix = ((img + color)/2).astype(np.int32)
			img = np.where(mask == 1, mix, img)

		for i in self.explorers:
			img[i.location] = np.array((255,255,255)) - img[i.location]

		implt = plt.imshow(img)
		plt.show()

	def generateExplorationPoints(self):
		width = self.picture.getWidth()
		height = self.picture.getHeight()

		points = PointGeneration.generateUniformPoints(width, height, values.identifier.generationPoints)
		print(points)
		return points


# pool = mp.Pool(2)
s = SurfaceIdentifier()
img = cv.imread('../testdata/3.png')
img = cv.resize(img, (96, 54), interpolation = cv.INTER_AREA)
# img = cv.resize(img, (192, 108), interpolation = cv.INTER_AREA)
# img = cv.resize(img, (48, 27), interpolation = cv.INTER_AREA)
rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
p = Picture(rgb)
s.setPicture(p)
ss = s.surfaceSet.createSurface()
#ss.addRect(10,10,100,100)
btcnt('whole')
s.identify()
etcnt('whole')
ptcnt('whole')
# ptcnt('iter')
# ptcnt('merge')
# ptcnt('bttl')
# pcnt('addEdge')
#pcnt('expandablePoints')
# print(s.surfaceSet.surfaces[1])
s.preview()  
