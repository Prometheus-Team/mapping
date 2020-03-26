
from fieldgenerator import *
from cloudset import *
from projector import *

class Projection:

	def __init__(self):
		self.cloudSet = CloudSet()
		self.projector = Projector()


	def project(self):
		pass



if __name__ == '__main__':

	m = ModelPreview()

	depth = genfromtxt('../testdata/depth2.csv', delimiter=',')
	cameraTransform = matrixTR((1,2,0),(0,50,40))

	p = Projector()
	p.openDepth(depth)
	points, normals = p.projectDepth(cameraTransform)

	c = CloudSet()
	c.infuseProjections(points, normals)


	colors = np.ones(points.shape)
	colors[np.all(normals == 0, axis=1)] = (1,0.5,0)

	normalProjections = points + normals/10
	normalDraw = np.concatenate((points, normalProjections), axis=1)

	m.addRenderable(Renderable(points, Renderable.POINTS, pointSize=3, color=colors))
	m.addRenderable(Renderable(normalDraw, Renderable.WIREFRAME, color=(0.1, 0.6,1)))
	m.addCamera(Camera(57, 43, cameraTransform))

	m.addRenderables(c.getCloudRenderables())

	m.start()
