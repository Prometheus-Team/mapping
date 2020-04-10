
from skimage import measure
import pymesh

from fieldgenerator import *
from cloudset import *
from projector import *


from vtk import (vtkSphereSource, vtkPolyData, vtkDecimatePro)

class Projection:

	def __init__(self):
		self.cloudSet = CloudSet()
		self.projector = Projector()

	def project(self):
		pass


# def decimation():
#     sphereS = vtkSphereSource()
#     sphereS.Update()

#     print(sphereS.GetOutput())

#     inputPoly = vtkPolyData()
#     inputPoly.ShallowCopy(sphereS.GetOutput())

#     print("Before decimation\n"
#           "-----------------\n"
#           "There are " + str(inputPoly.GetNumberOfPoints()) + "points.\n"
#           "There are " + str(inputPoly.GetNumberOfPolys()) + "polygons.\n")

#     decimate = vtkDecimatePro()
#     decimate.SetInputData(inputPoly)
#     decimate.SetTargetReduction(.10)
#     decimate.Update()

#     decimatedPoly = vtkPolyData()
#     decimatedPoly.ShallowCopy(decimate.GetOutput())

#     print("After decimation \n"
#           "-----------------\n"
#           "There are " + str(decimatedPoly.GetNumberOfPoints()) + "points.\n"
#           "There are " + str(decimatedPoly.GetNumberOfPolys()) + "polygons.\n")


if __name__ == '__main__':

	# decimation()

	m = ModelPreview()

	depth = genfromtxt('../testdata/depth3.csv', delimiter=',') * 10
	cameraTransform = matrixTR((-1,1,-1),(0,50,15))

	p = Projector()
	p.openDepth(depth)
	points, normals, edgePoints = p.projectDepth(cameraTransform)

	c = CloudSet()
	c.infuseProjections(points, normals)


	colors = np.ones(points.shape)
	colors[np.all(normals == 0, axis=1)] = (1,0.5,0)

	normalProjections = points + normals/10
	normalDraw = np.concatenate((points, normalProjections), axis=1)

	verts, faces, normals, values = measure.marching_cubes_lewiner(c.getCloud(), 0.1)
	
	normals = NormalEstimator.getMeshNormals(verts, faces)

	# normalProjections = verts + normals/10
	# normalDraw = np.concatenate((points, normalProjections), axis=1)

	np.savetxt('../testdata/blobverts.csv', verts)
	np.savetxt('../testdata/blobfaces.csv', faces)
	np.savetxt('../testdata/blobnormals.csv', normals)


	# mesh = pymesh.form_mesh(vertices, faces)

	# m.addRenderable(Renderable(points, Renderable.POINTS, pointSize=3, color=colors))
	# m.addRenderable(Renderable(normalDraw, Renderable.WIREFRAME, color=(0.1, 0.6,1)))
	m.addCamera(Camera(57, 43, cameraTransform))

	m.addRenderables(c.getCloudRenderables())

	print(verts)

	# m.addRenderable(Renderable(c.pointScaleDown(verts) - 3, Renderable.SOLID, indices=faces, normal=normals))

	time.sleep(1)

	m.start()
