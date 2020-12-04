
from skimage import measure

from mapping.image_projection.fieldgenerator import *
from mapping.image_projection.cloudset import *
from mapping.image_projection.projector import *
from mapping.image_projection.decimator import *

#from vtk import (vtkSphereSource, vtkPolyData, vtkDecimatePro)

class Projection:

	modelThreshold = 0.1

	def __init__(self):
		self.cloudSet = CloudSet()
		self.projector = Projector()
		self.decimator = Decimator()

	def project(self, depth, img, cameraTransform):
		self.projector.openDepth(depth)
		self.projector.openImage(img)
		points, normals, edgePoints = self.projector.projectDepth(cameraTransform)

		print("Bounds", bounds(0.5 + points/CloudSet.pointScale))

		self.cloudSet.cloudSetProjector.infuseProjections(points, normals)
		# self.cloudSet.cloudSetProjector.infuseEdgeProjections(edgePoints)

	def addWeightedProjection(self, projection, weight):
		self.cloudSet.mergeCloudSet(projection.cloudSet, weight)

	def getModel(self):
		cloudField = self.cloudSet.getCloud()
		verts, faces, normals, values = (np.array((), dtype=np.float32) for i in range(4))

		if np.any(cloudField > Projection.modelThreshold):
			verts, faces, normals, values = measure.marching_cubes(cloudField, Projection.modelThreshold)

		verts = self.compensateIndexNonNegativity(verts)
		# edges = self.cloudSet.getEdgeStrength(verts)
		# verts, faces, normals, edges = self.decimate(verts, faces, normals, edges, 3)

		return verts, faces, normals

	def compensateIndexNonNegativity(self, verts):

		minOrigins, maxOrigins = self.cloudSet.cloudMap.getMinAndMaxOrigins()
		return verts + minOrigins * self.cloudSet.resolution


	def getModelRenderable(self):
		verts, faces, normals = self.getModel()
		return Renderable(self.cloudSet.pointScaleDown(verts) - CloudSet.cloudScale, Renderable.SOLID, indices=faces, normal=normals)

	def decimate(self, verts, faces, normals, edges, iterations):

		for i in range(iterations):
			verts, faces, normals = self.decimator.collapse(verts, faces, normals, edges)
			edges = self.cloudSet.getEdgeStrength(verts)

		return verts, faces, normals, edges



if __name__ == '__main__':

	# decimation()

	m = ModelPreview()

	depth = genfromtxt('../testdata/depth3.csv', delimiter=',') * 10
	img = cv.imread('../testdata/ClippedDepthNormal.png')
	cameraTransform = matrixTR((-13,1,-1),(0,50,15))

	p = Projection()

	p.project(depth, img, cameraTransform)

	verts, faces, normals = p.getModel()

	# p = Projector()
	# c = CloudSet()
	# d = Decimator()
	
	# p.openImage(img)
	# p.openDepth(depth)
	# points, normals, edgePoints = p.projectDepth(cameraTransform)

	# c.cloudSetProjector.infuseProjections(points, normals)
	# c.cloudSetProjector.infuseEdgeProjections(edgePoints)

	# colors = np.ones(points.shape)
	# colors[np.all(normals == 0, axis=1)] = (1, 0.5, 0)

	# normalProjections = points + normals/10
	# normalDraw = np.concatenate((points, normalProjections), axis=1)

	# verts, faces, normals, values = measure.marching_cubes(c.getCloud(), 0.1)
	# edges = c.getEdgeStrength(verts)
	# print(edges[200:300])

	# print(edges[edges > 0])

	# verts, faces, normals, edges = d.decimate(verts, faces, normals, 3, edges)

	# normals = NormalEstimator.getMeshNormals(verts, faces)

	# normalProjections = verts + normals/10
	# normalDraw = np.concatenate((points, normalProjections), axis=1)

	# np.savetxt('../testdata/blobverts.csv', verts)
	# np.savetxt('../testdata/blobfaces.csv', faces)
	# np.savetxt('../testdata/blobnormals.csv', normals)
	

	# mesh = pymesh.form_mesh(vertices, faces)

	# m.addRenderable(Renderable(edgePoints[...,0:3], Renderable.POINTS, color=(0.1, 0.6,1)))
	# m.addRenderable(Renderable(points, Renderable.POINTS, pointSize=3, color=colors))
	# m.addRenderable(Renderable(normalDraw, Renderable.WIREFRAME, color=(0.1, 0.6,1)))
	m.addCamera(Camera(57, 43, cameraTransform))

	m.addRenderables(p.cloudSet.getCloudRenderables())

	# print(verts)
	# ptcnt('raver')

	# m.addRenderable(Renderable(p.cloudSet.pointScaleDown(verts) - 3, Renderable.SOLID, indices=faces, normal=normals))

	m.addRenderable(p.getModelRenderable())

	# verts, inds = RenderUtil.getBounds(p.cloudSet.getCloud())
	# m.addRenderable(Renderable(verts, Renderable.WIREFRAME, indices=inds, color=(1,0.8,1)))

	
	# m.addRenderable(Renderable(verts, Renderable.POINTS, pointSize=1, color=(verts + 1)/2))

	time.sleep(1)

	m.start()
