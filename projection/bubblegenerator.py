
import numpy as np
import pyrr

from util import *

class BubbleGenerator:

	def __init__(self, radius):
		self.radius = radius
		self.offset = [0,0,1]
		self.resolution = 10
		self.points = cube(self.resolution) * (self.radius * 1.1)

	def generateFieldLookup(self, vectors):
		fieldLookup = {}
		for i in vectors:
			self.offset = list(i)
			field = self.generate()
			fieldLookup[tuple(i)] = field
		return fieldLookup

	def generate(self):
		offset = pyrr.vector3.normalize(self.offset) * 1.5
		magnitude = (offset[0]**2 + offset[1]**2 + offset[2]**2)*1.2

		sphere = lambda x: min(max(self.radius - (x[0]**2 + x[1]**2 + x[2]**2), 0), self.radius) * 10
		sphereOffset = lambda x: min(max(magnitude - ((offset[0] - x[0])**2 + (offset[1] - x[1])**2 + (offset[2] - x[2])**2), 0), magnitude) * 10

		sphereStrength = np.apply_along_axis(sphere, 1, self.points)
		sphereOffsetStrength = np.apply_along_axis(sphereOffset, 1, self.points)
		strength = (sphereOffsetStrength * sphereStrength).reshape(self.points.shape[0], 1)/10
		return strength
