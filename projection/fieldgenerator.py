
import numpy as np
import pyrr

from util import *
from previewer import *
from normalestimator import *

class R:

	vectorExtent = 1

class FieldGenerator:

	def __init__(self, radius, resolution):
		self.radius = radius
		self.resolution = resolution
		self.points = (cube(self.resolution) * (self.radius * 1.1)).reshape((-1,3))


class FullBubbleGenerator(FieldGenerator):

	def __init__(self, radius, resolution):
		super(FullBubbleGenerator, self).__init__(radius, resolution)
		self.bubble = self.generate()

	def generate(self):
		sphere = lambda x: min(max(self.radius - (x[0]**2 + x[1]**2 + x[2]**2), 0), self.radius) * 10

		sphereStrength = np.apply_along_axis(sphere, 1, self.points)
		strength = sphereStrength
		strength = strength.reshape((self.resolution, self.resolution, self.resolution))		

		return strength

	def getMultiField(self, points):
		return self.bubble


class SemiBubbleGenerator(FieldGenerator):

	def __init__(self, radius, resolution):
		super(SemiBubbleGenerator, self).__init__(radius, resolution)
		self.offset = [0,0,1]
		self.vectors = self.generateVectors(R.vectorExtent)
		self.fieldLookup = self.generateMultiFieldLookup()

	def extentIndex(self, vectorValue):
		return R.vectorExtent + vectorValue

	def vectorShape(self):
		extent = (self.extentIndex(R.vectorExtent)) + 1
		return (extent, extent, extent, self.resolution, self.resolution, self.resolution)

	def generateMultiFieldLookup(self):
		multiFieldLookup = np.zeros(self.vectorShape())

		for i in self.vectors:
			offset = tuple(i)
			field = self.generate(offset)
			multiFieldLookup[i[0],i[1],i[2]] = field

		return multiFieldLookup

	def generateVectors(self, extent):
		axisValues = np.linspace(-extent, extent, 2*extent + 1)
		vectors = pair3(axisValues, axisValues, axisValues)
		vectors = vectors[(np.logical_not((vectors == 0).all(axis=1)))]
		return vectors.astype(np.int32)

	def getMultiField(self, normals):
		# print(vector)
		normals = normals.reshape((-1, 3))
		normals = NormalEstimator.normalize(normals) * R.vectorExtent
		# print(vector)
		roundedNormals = np.rint(normals).astype(np.int32)
		fields = self.fieldLookup[roundedNormals[:,0], roundedNormals[:,1], roundedNormals[:,2]]
		return fields

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



if __name__ == '__main__':
	c = SemiBubbleGenerator(1, 7)
	f = FullBubbleGenerator(1, 5)
	m = ModelPreview()
	m.start()

	vector = np.array((0,0.1,0.3))
	m.addRenderable(Renderable(c.points, Renderable.POINTS, pointSize=c.getMultiField(vector)))
	m.addRenderable(Renderable(np.array([(0,0,0),vector], dtype=np.float32), Renderable.WIREFRAME, renderType=GL_LINE_LOOP, pointSize=5, color=(1,0.5,0)))
