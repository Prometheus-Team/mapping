
import numpy as np
import pyrr

from util import *

class BubbleGenerator:

	def __init__(self, radius, resolution):
		self.radius = radius
		self.offset = [0,0,1]
		self.resolution = resolution
		self.points = cube(self.resolution) * (self.radius * 1.1)
		self.points = self.points.reshape((-1,3))

	def generateFieldLookup(self, vectors):
		fieldLookup = {}
		for i in vectors:
			offset = tuple(i)
			field = self.generate(offset)
			fieldLookup[offset] = field
		return fieldLookup

	def generate(self, offset):
		offset = pyrr.vector3.normalize(offset) * 1.5
		magnitude = (offset[0]**2 + offset[1]**2 + offset[2]**2)*1.2

		sphere = lambda x: min(max(self.radius - (x[0]**2 + x[1]**2 + x[2]**2), 0), self.radius) * 10
		sphereOffset = lambda x: (min(max(magnitude - ((offset[0] - x[0])**2 + (offset[1] - x[1])**2 + (offset[2] - x[2])**2), 0), magnitude) ** 0.5) * 10

		sphereStrength = np.apply_along_axis(sphere, 1, self.points)
		sphereOffsetStrength = np.apply_along_axis(sphereOffset, 1, self.points)
		strength = (sphereOffsetStrength * sphereStrength)/10
		strength = strength.reshape((self.resolution, self.resolution, self.resolution))		

		return strength
