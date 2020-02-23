import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import time
import random
import cv2 as cv
import multiprocessing as mp


from surface import *
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
		# points  = self.generateExplorationPoints()
		# print(points)
		# for i in points:
		for i in [(30, 30),(60, 40)]:#, (27, 13)]:
			if not self.surfaceSet.isContained(i):
				explorer = Explorer(i, self.surfaceSet)
				explorer.declareSurface()
				self.explorers.append(explorer)


	def startExploration(self):
		print("exploring")

		# result = [pool.apply(Explorer.explore, args=(i, 4, 8)) for i in self.explorers]
		Explorer.initializeSpots(self.surfaceSet.picture.getWidth(), self.surfaceSet.picture.getHeight())
		for i in self.explorers:
			i.explore()

	def isExplorationComplete(self):
		totalArea = self.picture.getWidth() * self.picture.getHeight()
		exploredArea = self.surfaceSet.getTotalCoverage()
		return exploredArea/totalArea > values.identifier.explorationThreshold
		
	def preview(self):
		print(len(self.surfaceSet.surfaces))

		img = np.copy(self.picture.rgb)

		for i in range(img.shape[1]):
			for j in range(img.shape[0]):
				cont = False
				for k in self.explorers:
					if k.location == (i, j):
						img[j][i] = np.array((200,200,200))
						cont = True
						break
				if cont:
					continue
				for k in self.surfaceSet.surfaces:
					if k.contains(Point(i, j)):
						img[j][i] = img[j][i]/2 + np.array(k.color)/2

		implt = plt.imshow(img)

		plt.show()

	def generateExplorationPoints(self):
		width = self.picture.getWidth()
		height = self.picture.getHeight()

		points = PointGeneration.generateRandomizedUniformPoints(width, height, values.identifier.generationPoints, 1)

		return points


# pool = mp.Pool(2)
s = SurfaceIdentifier()
img = cv.imread('../testdata/2.png')
img = cv.resize(img, (96, 72), interpolation = cv.INTER_AREA)
rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
p = Picture(rgb)
s.setPicture(p)
ss = s.surfaceSet.createSurface()
#ss.addRect(10,10,100,100)
btcnt('whole')
s.identify()
etcnt('whole')
ptcnt('whole')
ptcnt('iter')
ptcnt('bttl')
# pcnt('addEdge')
#pcnt('expandablePoints')
# print(s.surfaceSet.surfaces[1])
s.preview()  
