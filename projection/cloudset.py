
import numpy as np
import pyrr

from util import *

class CloudSet:

	def __init__(self):
		self.clouds = []


class Cloud:

	def __init__(self):
		self.bounds = np.array(((100,200),(0,100),(100,200)))
		self.volume = np.zeros(self.getSize())
		self.matrix = pyrr.Matrix44.from_translation()

	def getSize(self):
		return self.bounds[:,1] - self.bounds[:,0]

	def getOffset(self):
		return self.bounds[:,0]

	def getBoundsRenderable(self):
		pass

	def localize(self, point):
		pass


