import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import time
import random
import cv2 as cv

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
		#for i in self.generateExplorationPoints():
		for i in [(15, 15),(30, 20)]:
			if not self.surfaceSet.isContained(i):
				explorer = Explorer(i, self.surfaceSet)
				explorer.declareSurface()
				self.explorers.append(explorer)


	def startExploration(self):
		print("exploring")
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

s = SurfaceIdentifier()
img = cv.imread('../testdata/2.png')
img = cv.resize(img, (48, 36), interpolation = cv.INTER_AREA)
rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
p = Picture(rgb)
s.setPicture(p)
ss = s.surfaceSet.createSurface()
#ss.addRect(10,10,100,100)
t = time.time()
s.identify()
print(time.time() - t)
pcnt('expandablePoints')
s.preview()
