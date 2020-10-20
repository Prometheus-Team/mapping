
from skimage import measure
import pymesh

from fieldgenerator import *
from cloudset import *
from projector import *
from decimator import *


#from vtk import (vtkSphereSource, vtkPolyData, vtkDecimatePro)

class Projection:

	def __init__(self):
		self.cloudSet = CloudSet()
		self.projector = Projector()

	def project(self):
		pass

if __name__ == '__main__':

	# decimation()

	m = ModelPreview()

	depth = genfromtxt('../testdata/depth3.csv', delimiter=',') * 10
	img = cv.imread('../testdata/ClippedDepthNormal.png')
	cameraTransform = matrixTR((-1,1,-1),(0,50,15))

	p = Projector()
	c = CloudSet()
	d = Decimator()
	
	btcnt('raver')

	p.openImage(img)
	p.openDepth(depth)
	points, normals, edgePoints = p.projectDepth(cameraTransform)

	c.infuseProjections(points, normals)
	c.infuseEdgeProjections(edgePoints)

	etcnt('raver')

	colors = np.ones(points.shape)
	colors[np.all(normals == 0, axis=1)] = (1, 0.5, 0)

	normalProjections = points + normals/10
	normalDraw = np.concatenate((points, normalProjections), axis=1)

	verts, faces, normals, values = measure.marching_cubes(c.getCloud(), 0.1)
	edges = c.getEdgeStrength(verts)
	print(edges[200:300])

	print(edges[edges > 0])

	verts, faces, normals = d.collapse(verts, faces, normals, edges)
	edges = c.getEdgeStrength(verts)
	verts, faces, normals = d.collapse(verts, faces, normals, edges)
	edges = c.getEdgeStrength(verts)
	verts, faces, normals = d.collapse(verts, faces, normals, edges)

	normals = NormalEstimator.getMeshNormals(verts, faces)

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

	m.addRenderables(c.getCloudRenderables())

	# print(verts)
	ptcnt('raver')

	m.addRenderable(Renderable(c.pointScaleDown(verts) - 3, Renderable.SOLID, indices=faces, normal=normals))

	time.sleep(1)

	m.start()
