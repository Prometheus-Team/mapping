from projection import *
from obj_exporter import *

class Aggregate:

	def __init__(self):
		self.frames = []
		self.projection = Projection()

	def addFrame(self, frame):
		self.frames.append(frame)
		weight = 1/len(self.frames)
		self.projection.addWeightedProjection(frame.projection, weight)

class Frame:

	def __init__(self, image, depth, cameraTransform):
		self.image = image
		self.depth = depth
		self.cameraTransform = cameraTransform
		self.projection = Projection()

		self.projection.project(depth, img, cameraTransform)

	def getCamera(self):
		return Camera(57, 43, self.cameraTransform)


if __name__ == '__main__':

	depth = genfromtxt('../testdata/depth3.csv', delimiter=',') * 10
	img = cv.imread('../testdata/ClippedDepthNormal.png')
	cameraTransform1 = matrixTR((-1,1,-1),(0,50,15))
	cameraTransform2 = matrixTR((-1,10,-1),(0,40,15))

	m = ModelPreview()
	a = Aggregate()

	f1 = Frame(img, depth, cameraTransform1)
	f2 = Frame(img, depth, cameraTransform2)

	a.addFrame(f1)
	a.addFrame(f2)

	m.addRenderable(a.projection.getModelRenderable())

	m.addCamera(f1.getCamera())
	# m.addCamera(f2.getCamera())

	m.addRenderables(a.projection.cloudSet.getCloudRenderables())

	time.sleep(1)

	m.start()


	OBJExporter.exportModel(a.projection.getModel(), "Igno2")