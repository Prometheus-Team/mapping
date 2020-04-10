
import numpy as np
import pyrr

from util import *
from previewer import *
from bubblegenerator import *
from normalestimator import *


class FieldGenerator:

	def __init__(self, generator, resolution):
		self.fieldLookup = {}
		self.generator = generator(1, resolution)
		self.generateFieldLookup()

	def getField(self, vector):
		# print(vector)
		vector = pyrr.vector3.normalize(vector)
		# print(vector)
		roundedVector = (round(vector[0]), round(vector[1]), round(vector[2]))
		return self.fieldLookup[tuple(roundedVector)]

	def getMultiField(self, normals):
		# print(vector)
		normals = NormalEstimator.normalize(normals)
		# print(vector)
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
		return self.generator.generateFieldLookup(vectors)


if __name__ == '__main__':
	c = FieldGenerator(SemiBubbleGenerator, 7)
	m = ModelPreview()
	m.start()

	vector = (0,0.1,0.3)
	m.addRenderable(Renderable(c.generator.points, Renderable.POINTS, pointSize=c.getField(vector)))
	m.addRenderable(Renderable(np.array([(0,0,0),vector], dtype=np.float32), Renderable.WIREFRAME, renderType=GL_LINE_LOOP, pointSize=5, color=(1,0.5,0)))

