
import numpy as np
import pyrr

from util import *
from previewer import *

class CloudGenerator:

	def __init__(self):
		self.fieldLookup = {}
		self.fieldGenerator = BubbleGenerator(1)
		self.generateFieldLookup()

	def getField(self, vector):
		vector = pyrr.vector3.normalize(vector)
		roundedVector = (round(vector[0]), round(vector[1]), round(vector[2]))
		return self.fieldLookup[tuple(roundedVector)]

	def generateFieldLookup(self):
		vectors = self.generateVectors(1)
		self.fieldLookup = self.generateFieldsFrom(vectors)


	def generateVectors(self, extent):
		axisValues = np.linspace(-extent, extent, 2*extent + 1)
		vectors = pair3(axisValues, axisValues, axisValues)
		vectors = vectors[(np.logical_not((vectors == 0).all(axis=1)))]
		return vectors


	def generateFieldsFrom(self, vectors):
		return self.fieldGenerator.generateFieldLookup(vectors)


class BubbleGenerator:

	def __init__(self, radius):
		self.radius = radius
		self.offset = [0,0,1]
		self.resolution = 8
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


if __name__ == '__main__':
	c = CloudGenerator()
	m = ModelPreview()
	m.start()

	vector = (0,0.1,0.3)
	m.addRenderable(Renderable(c.fieldGenerator.points, Renderable.POINTS, pointSize=c.getField(vector)))
	m.addRenderable(Renderable(np.array([(0,0,0),vector], dtype=np.float32), Renderable.WIREFRAME, color=(1,0.5,0)))

