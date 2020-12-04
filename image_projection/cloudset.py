
import numpy as np
import pyrr

from mapping.image_projection.util import *
from mapping.image_projection.previewer import *
from mapping.image_projection.fieldgenerator import *

from client_data import ClientData

CloudSetValues = ClientData.cloudValues

class CloudSet:

	fieldResolution = 7
	edgeFieldResolution = 5
	cloudSetResolution = 100
	cloudScale = 3
	pointScale = 6
	cloudVolumeColor = (0.5,1,0.8)
	cloudBoundsColor = (1,0.4,1)
	cloudEdgeColor = (0.9,0.8,0.4)

	def __init__(self):
		self.resolution = CloudSetValues.cloudSetResolution
		self.cloudScale = CloudSetValues.cloudScale
		self.pointScale = CloudSetValues.pointScale

		#locations of the points the clouds affect
		self.points = cube(self.resolution) * self.resolution
		self.cloudMap = CloudMap(self)
		self.clouds = [Cloud(self, (0,0,0))]
		self.cloudSetProjector = CloudSetProjector(self)

	def addCloud(self, origin):
		self.clouds.append(Cloud(self, origin))

	def getCloudWithOrigin(self, origin):
		for i in self.clouds:
			# print(i.origin, origin, i.origin == origin)
			if np.all(i.origin == origin):
				return i

	def getPoints(self, cloud):
		return self.points + cloud.origin * self.resolution

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
			edgeStrength += i.getCloudEdgeStrength(points)

		# edgeStrength /= np.max(edgeStrength) if np.max(edgeStrength) != 0 else 1
		return edgeStrength

	def getCloudRenderables(self):
		renderables = []
		for i in self.clouds:
			# renderables.append(i.getVolumeRenderable())
			# renderables.append(i.getEdgeRenderable())
			renderables.append(i.getBoundsRenderable())
		return renderables

	def getCloud(self):
		cloudSize = self.cloudMap.getFullCloudSize()
		size = cloudSize * self.resolution
		print("size", size)

		volume = np.zeros(size)
		startOrigin, endOrigin = self.cloudMap.getMinAndMaxOrigins()
		startResolutionOrigin = startOrigin * self.resolution

		for i in self.clouds:
			minResolutionOrigin = ((i.origin * self.resolution) - startResolutionOrigin).astype(np.int32)
			maxResolutionOrigin = (((i.origin + 1) * self.resolution) - startResolutionOrigin).astype(np.int32)
			print("from", minResolutionOrigin, "to", maxResolutionOrigin)
			volume[minResolutionOrigin[0]:maxResolutionOrigin[0], minResolutionOrigin[1]:maxResolutionOrigin[1], minResolutionOrigin[2]:maxResolutionOrigin[2]] = i.volume

		return volume

	def mergeCloudSet(self, cloudSet, weight):
		self.addMissingCloudsFrom(cloudSet)

		# for i in self.clouds:
		# 	print("Cloud Origin:", i.origin)

		for i in self.clouds:
			toMerge = cloudSet.getCloudWithOrigin(i.origin)
			# print("Merge",i,"with",toMerge,"of origin", i.origin)
			if toMerge != None:
				i.mergeCloud(toMerge, weight)

	def addMissingCloudsFrom(self, cloudSet):

		for i in cloudSet.clouds:
			if (self.getCloudWithOrigin(i.origin) == None):
				self.addCloud(i.origin)

	def getCloudsAffected(self, points):
		for i in self.clouds:
			pass


class CloudSetProjector:

	def __init__(self, cloudSet):
		self.cloudSet = cloudSet
		self.fieldGenerator = SemiBubbleGenerator(1, CloudSetValues.fieldResolution)
		self.edgeFieldGenerator = FullBubbleGenerator(1, CloudSetValues.edgeFieldResolution)

	def infuseProjections(self, points, normals):

		scaledPoints = 0.5 + points/CloudSetValues.pointScale
		pointBounds = bounds(scaledPoints)
		blocks = self.getBlocksIn(pointBounds)

		print("Blocks", blocks)

		for i in blocks:
			self.cloudSet.addCloud(i)

		points = points.reshape((-1,3))
		normals = normals.reshape((-1,3))

		points, normals = self.removeEmptyNormals(points, normals)
		# points = self.approximatePoints(points)
		fields = self.fieldGenerator.getMultiField(normals)
		# fields = [self.fieldGenerator.getField(i) for i in normals]

		for i in self.cloudSet.clouds:
			i.cloudProjector.addProjections(fields, points)

	def infuseEdgeProjections(self, edgePoints):
		edgePoints = edgePoints.reshape((-1,4))[...,0:3]

		field = self.edgeFieldGenerator.getMultiField(edgePoints)
		for i in self.cloudSet.clouds:
			i.cloudProjector.addEdgeProjections(field, edgePoints)

	def getBlocksIn(self, bounds):

		bounds = np.array(bounds)
		bounds[0] = np.floor(bounds[0])
		bounds[1] = np.ceil(bounds[1])

		print("Exp Bounds", bounds)

		xList = np.arange(bounds[0][0], bounds[1][0]).astype(dtype=np.int32)
		yList = np.arange(bounds[0][1], bounds[1][1]).astype(dtype=np.int32)
		zList = np.arange(bounds[0][2], bounds[1][2]).astype(dtype=np.int32)

		# zero = np.zeros(1).astype(dtype= np.int32)

		# if (len(xList) == 0):
		# 	xList = zero

		# if (len(yList) == 0):
		# 	yList = zero

		# if (len(zList) == 0):
		# 	zList = zero

		return pair3(zList, xList, yList)

	def approximatePoints(self, points):
		points = np.rint(self.pointScaleUp(points)).astype(dtype=np.int32)
		return points

	def removeEmptyNormals(self, points, normals):
		condition = np.logical_not(np.all(normals == 0, axis=1))

		points = points[condition]
		normals = normals[condition]

		return points, normals

class CloudMap:

	def __init__(self, cloudSet):
		self.cloudSet = cloudSet

	def getClouds(self):
		return self.cloudSet.clouds

	def getOrigins(self):
		origins = []
		for i in self.cloudSet.clouds:
			origins.append(i.origin)
		return origins

	def getMinAndMaxOrigins(self):
		origins = np.array(self.getOrigins())
		minOrigins = origins.min(axis = 0)
		maxOrigins = origins.max(axis = 0)
		return minOrigins, maxOrigins

	def getFullCloudSize(self):
		minOrigin, maxOrigin = self.getMinAndMaxOrigins()
		size = (maxOrigin - minOrigin) + 1
		return size.astype(np.int32)

	def getCenteredCloudField(self, cloudField):
		origins = np.array(self.getOrigins())
		minOrigins = origins.min(axis = 1)
		maxOrigins = origins.max(axis = 1)
		return cloudField - maxOrigins


class Cloud:
	
	rawCenter = np.array((0.5, 0.5, 0.5))

	def __init__(self, cloudSet, origin):
		self.cloudSet = cloudSet
		self.origin = np.array(origin)
		self.center = np.array(origin) + Cloud.rawCenter
		self.volume = np.zeros(self.getSize())
		self.edge = np.zeros(self.getSize())
		self.cloudProjector = CloudProjector(self)

	def offset(self, points):
		return points + self.origin * self.cloudSet.pointScaleDown(self.cloudSet.resolution)

	def deoffset(self, points):
		return points

	def getSize(self):
		return np.array((self.cloudSet.resolution, self.cloudSet.resolution, self.cloudSet.resolution))

	def getBounds(self):
		return (self.center - self.getSize()/2, self.center + self.getSize()/2)

	def getPointIndex(self, points):
		return np.rint((points/CloudSetValues.pointScale + Cloud.rawCenter) * self.cloudSet.resolution).astype(dtype=np.int32)

	def getCloudEdgeStrength(self, points):
		points = np.rint(points).astype(dtype=np.int32)
		bounds = self.getBounds()
		# print(bounds)
		nullPoints = np.any(np.logical_or(points > self.getSize(), points < np.array([[0,0,0]])), axis=1)
		points[nullPoints] = 0
		print(points.size)
		edgeStrength = self.edge[points[:,0], points[:,1], points[:,2]]
		# print(self.edge)
		edgeStrength[nullPoints] = 0
		# print(edgeStrength)
		return edgeStrength

	def getVolumeRenderable(self):
		points = self.offset(self.cloudSet.getCloudScaledPoints())
		return Renderable(points, Renderable.POINTS, pointSize = self.volume/20, color=CloudSetValues.cloudVolumeColor)

	def getEdgeRenderable(self):
		points = self.offset(self.cloudSet.getCloudScaledPoints())
		return Renderable(points, Renderable.POINTS, pointSize = self.edge/10, color=CloudSetValues.cloudEdgeColor)

	def getBoundsRenderable(self):
		verts, inds = RenderUtil.getBounds(self.offset(self.cloudSet.getCloudScaledPoints()))
		return Renderable(verts, Renderable.WIREFRAME, indices=inds, color=CloudSetValues.cloudBoundsColor)

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

	def mergeCloud(self, cloud, weight):

		print(1 - weight)
		print(weight)

		self.volume = (1 - weight) * self.volume + weight * cloud.volume
		self.edge = (1 - weight) * self.edge + weight * cloud.edge



class CloudProjector:

	def __init__(self, cloud):
		self.cloud = cloud

	def addProjections(self, fields, points):
		# self.addMultiProjection(fields, points)
		for i in range(points.shape[0]):
			self.addProjection(fields[i], points[i])

	# def addMultiProjection(self, fields, points):
	# 	points = np.rint((points/CloudSetValues.pointScale + self.origin) * self.cloudSet.resolution).astype(dtype=np.int32)
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

		point = self.cloud.getPointIndex(point - (self.cloud.origin * CloudSetValues.pointScale))
		fieldShape = field.shape
		vb, fb = self.cloud.getVolumeField(point, fieldShape)


		if (np.any(vb < 0) or np.any(fb < 0)):
			return

		self.cloud.volume[vb[0][0]:vb[0][1], vb[1][0]:vb[1][1], vb[2][0]:vb[2][1]] += field[fb[0][0]:fb[0][1], fb[1][0]:fb[1][1], fb[2][0]:fb[2][1]]


	def addEdgeProjections(self, field, points):
		# self.addMultiProjection(fields, points)
		for i in range(points.shape[0]):
			self.addEdgeProjection(field, points[i])

	def addEdgeProjection(self, field, point):

		# print(point)
		point = np.rint((point/CloudSetValues.pointScale + self.cloud.center) * self.cloud.cloudSet.resolution).astype(dtype=np.int32)
		fieldShape = field.shape
		vb, fb = self.cloud.getVolumeField(point, fieldShape)

		# print(point)
		if (np.any(vb < 0) or np.any(fb < 0)):
			# print("Point", point)
			return

		# print(vb, fb, "\n")

		self.cloud.edge[vb[0][0]:vb[0][1], vb[1][0]:vb[1][1], vb[2][0]:vb[2][1]] += field[fb[0][0]:fb[0][1], fb[1][0]:fb[1][1], fb[2][0]:fb[2][1]]

CloudSetValues = CloudSet


if __name__ == '__main__':

	# m = ModelPreview()
	# c = CloudSet()
	# points = np.array(((1,0,0),(0,2,0),(0,0,3)))/2
	# # c.infuseProjections(points, np.array(((0,1,0),(0,-1,0),(0,1,0))))
	# # c.infuseProjections(np.array(((1,1,2))), np.array(((1,-1,1))))
	# c.cloudSetProjector.infuseProjections(np.array(((1,1,2))), np.array(((0,1,0))))
	# c.cloudSetProjector.infuseEdgeProjections(cube(4)*2)

	# edgeStrength = c.getEdgeStrength(np.array([[0,0,0],[3,3.7,4.8]]))
	# # print(edgeStrength)

	# m.addRenderables(c.getCloudRenderables())
	# m.addRenderable(Renderable(np.array(((1,1,2))), Renderable.POINTS, pointSize=4, color=(0,1,0)))
	# # m.addRenderable(Renderable(rotate(points, (90, 0, 90)), Renderable.POINTS, pointSize=4, color=(0,1,0)))

	# m.start()

	# # print(cube(2))

	print(CloudSetProjector.getBlocksIn(((-0.2,0.1,0.1),(4,2,3))))



