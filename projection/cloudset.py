
import numpy as np
import pyrr

from util import *
from previewer import *
from fieldgenerator import *

class R:

	fieldResolution = 7
	edgeFieldResolution = 5
	cloudSetResolution = 100
	cloudResolution = 50
	cloudScale = 3
	pointScale = 6
	cloudVolumeColor = (0.5,1,0.8)
	cloudBoundsColor = (1,0.4,1)
	cloudEdgeColor = (0.9,0.8,0.4)


class CloudSet:

	def __init__(self):
		self.resolution = R.cloudSetResolution
		self.cloudScale = R.cloudScale
		self.pointScale = R.pointScale

		#locations of the points the clouds affect
		self.points = cube(self.resolution) * self.resolution
		self.clouds = [Cloud(self, (0, 0, 0))]
		self.fieldGenerator = SemiBubbleGenerator(1, R.fieldResolution)
		self.edgeFieldGenerator = FullBubbleGenerator(1, R.edgeFieldResolution)

	def cloudScaleDown(self, points):
		return (points/self.resolution) * self.cloudScale

	def cloudScaleUp(self, points):
		return (points/self.cloudScale) * self.resolution

	def pointScaleDown(self, points):
		return (points/self.resolution) * self.pointScale

	def pointScaleUp(self, points):
		return (points/self.pointScale) * self.resolution

	def getCloudScaledPoints(self):
		return self.cloudScaleDown(self.points)

	def getEdgeStrength(self, points):
		edgeStrength = np.zeros(points.shape[0]).astype(np.float32)
		for i in self.clouds:
			edgeStrength += i.getEdgeStrength(points)

		# edgeStrength /= np.max(edgeStrength) if np.max(edgeStrength) != 0 else 1
		return edgeStrength

	def infuseProjections(self, points, normals):
		points = points.reshape((-1,3))
		normals = normals.reshape((-1,3))

		points, normals = self.removeEmptyNormals(points, normals)
		# points = self.approximatePoints(points)
		fields = self.fieldGenerator.getMultiField(normals)
		# fields = [self.fieldGenerator.getField(i) for i in normals]

		for i in self.clouds:
			i.addProjections(fields, points)

	def infuseEdgeProjections(self, edgePoints):
		edgePoints = edgePoints.reshape((-1,4))[...,0:3]

		field = self.edgeFieldGenerator.getMultiField(edgePoints)
		for i in self.clouds:
			i.addEdgeProjections(field, edgePoints)


	def approximatePoints(self, points):
		points = np.rint(self.pointScaleUp(points)).astype(dtype=np.int32)
		return points

	def removeEmptyNormals(self, points, normals):
		condition = np.logical_not(np.all(normals == 0, axis=1))

		points = points[condition]
		normals = normals[condition]

		return points, normals

	def getCloudRenderables(self):
		renderables = []
		for i in self.clouds:
			renderables.append(i.getVolumeRenderable())
			renderables.append(i.getEdgeRenderable())
			renderables.append(i.getBoundsRenderable())
		return renderables

	def getCloud(self):
		return self.cloudScaleDown(self.clouds[0].volume)

	def getCloudsAffected(self, points):
		for i in self.clouds:
			pass


class Cloud:

	def __init__(self, cloudSet, origin):
		self.cloudSet = cloudSet
		self.origin = np.array(origin) + (0.5,0.5,0.5)
		self.volume = np.zeros(self.getSize())
		self.edge = np.zeros(self.getSize())

	def getSize(self):
		resolution = R.cloudResolution;
		return np.array((self.cloudSet.resolution, self.cloudSet.resolution, self.cloudSet.resolution))

	def getBounds(self):
		return (self.origin - self.getSize()/2, self.origin + self.getSize()/2)

	def getPointIndex(self, points):
		return np.rint((points/R.pointScale + self.origin) * self.cloudSet.resolution).astype(dtype=np.int32)

	def getEdgeStrength(self, points):
		points = np.rint(points).astype(dtype=np.int32)
		bounds = self.getBounds()
		print(bounds)
		nullPoints = np.any(np.logical_or(points > self.getSize(), points < np.array([[0,0,0]])), axis=1)
		points[nullPoints] = 0
		edgeStrength = self.edge[points[:,0], points[:,1], points[:,2]]
		# print(self.edge)
		edgeStrength[nullPoints] = 0
		# print(edgeStrength)
		return edgeStrength

	def getVolumeRenderable(self):
		points = self.cloudSet.getCloudScaledPoints()
		return Renderable(points, Renderable.POINTS, pointSize = self.volume/20, color=R.cloudVolumeColor)

	def getEdgeRenderable(self):
		points = self.cloudSet.getCloudScaledPoints()
		return Renderable(points, Renderable.POINTS, pointSize = self.edge/10, color=R.cloudEdgeColor)

	def getBoundsRenderable(self):
		verts, inds = RenderUtil.getBounds(self.cloudSet.getCloudScaledPoints())
		return Renderable(verts, Renderable.WIREFRAME, indices=inds, color=R.cloudBoundsColor)

	def getVolumeField(self, point, fieldShape):
		fieldBounds = np.array(((0,fieldShape[2]),(0,fieldShape[1]),(0,fieldShape[0])), dtype=np.int32)
		fieldShape = np.array(fieldShape)

		extent = (fieldShape - 1)/2
		volumeBounds = np.array([point - extent, point + extent + 1], dtype=np.int32).T
		actualVolumeBounds = np.array(((0,self.volume.shape[2]),(0,self.volume.shape[1]),(0,self.volume.shape[0])), dtype=np.int32)

		extras = np.minimum((volumeBounds*(1,-1)) + actualVolumeBounds, 0) * (-1,1)

		# print(volumeBounds, fieldBounds, extras, "\n")

		volumeBounds += extras
		fieldBounds += extras

		# print(volumeBounds, fieldBounds, "\n")

		return volumeBounds, fieldBounds

	def addProjections(self, fields, points):
		# self.addMultiProjection(fields, points)
		for i in range(points.shape[0]):
			self.addProjection(fields[i], points[i])

	# def addMultiProjection(self, fields, points):
	# 	points = np.rint((points/R.pointScale + self.origin) * self.cloudSet.resolution).astype(dtype=np.int32)
	# 	fieldShape = fields.shape

	# 	fieldBounds = np.array(((0,fieldShape[2]),(0,fieldShape[1]),(0,fieldShape[0])), dtype=np.int32)
	# 	fieldShape = np.array(fieldShape)

	# 	extent = (fieldShape - 1)/2

	# 	volumeBounds = np.array([points - extent, points + extent + 1], dtype=np.int32).T
	# 	actualVolumeBounds = np.array(((0,self.volume.shape[2]),(0,self.volume.shape[1]),(0,self.volume.shape[0])), dtype=np.int32)

	# 	extras = np.minimum((volumeBounds*(1,-1)) + actualVolumeBounds, 0) * (-1,1)

	# 	# print(volumeBounds, fieldBounds, extras, "\n")

	# 	volumeBounds += extras
	# 	fieldBounds += extras

	# 	if (np.any(volumeBounds < 0) or np.any(fieldBounds < 0)):
	# 		return

	# 	self.volume[vb[0][0]:vb[0][1], vb[1][0]:vb[1][1], vb[2][0]:vb[2][1]] += field[fb[0][0]:fb[0][1], fb[1][0]:fb[1][1], fb[2][0]:fb[2][1]]


	def addProjection(self, field, point):

		point = self.getPointIndex(point)
		fieldShape = field.shape
		vb, fb = self.getVolumeField(point, fieldShape)


		if (np.any(vb < 0) or np.any(fb < 0)):
			return

		self.volume[vb[0][0]:vb[0][1], vb[1][0]:vb[1][1], vb[2][0]:vb[2][1]] += field[fb[0][0]:fb[0][1], fb[1][0]:fb[1][1], fb[2][0]:fb[2][1]]


	def addEdgeProjections(self, field, points):
		# self.addMultiProjection(fields, points)
		for i in range(points.shape[0]):
			self.addEdgeProjection(field, points[i])

	def addEdgeProjection(self, field, point):

		# print(point)
		point = np.rint((point/R.pointScale + self.origin) * self.cloudSet.resolution).astype(dtype=np.int32)
		fieldShape = field.shape
		vb, fb = self.getVolumeField(point, fieldShape)

		# print(point)
		if (np.any(vb < 0) or np.any(fb < 0)):
			# print("Point", point)
			return

		# print(vb, fb, "\n")

		self.edge[vb[0][0]:vb[0][1], vb[1][0]:vb[1][1], vb[2][0]:vb[2][1]] += field[fb[0][0]:fb[0][1], fb[1][0]:fb[1][1], fb[2][0]:fb[2][1]]


if __name__ == '__main__':

	m = ModelPreview()
	c = CloudSet()
	points = np.array(((1,0,0),(0,2,0),(0,0,3)))/2
	# c.infuseProjections(points, np.array(((0,1,0),(0,-1,0),(0,1,0))))
	# c.infuseProjections(np.array(((1,1,2))), np.array(((1,-1,1))))
	c.infuseProjections(np.array(((1,1,2))), np.array(((0,1,0))))
	c.infuseEdgeProjections(cube(4)*2)

	edgeStrength = c.getEdgeStrength(np.array([[0,0,0],[3,3.7,4.8]]))
	print(edgeStrength)

	m.addRenderables(c.getCloudRenderables())
	m.addRenderable(Renderable(np.array(((1,1,2))), Renderable.POINTS, pointSize=4, color=(0,1,0)))
	# m.addRenderable(Renderable(rotate(points, (90, 0, 90)), Renderable.POINTS, pointSize=4, color=(0,1,0)))

	m.start()

	print(cube(2))



