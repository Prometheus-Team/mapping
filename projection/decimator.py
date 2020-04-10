
import numpy as np

from previewer import *

class R:

	dotThreshold = 0.7

class Decimator:


	def __init__(self):
		pass



if __name__=='__main__':

	m = ModelPreview()

	m.start()

	verts = np.genfromtxt('../testdata/blobverts.csv')
	faces = np.genfromtxt('../testdata/blobfaces.csv')
	normals = np.genfromtxt('../testdata/blobnormals.csv')

	m.addRenderable(Renderable(((verts/100)*6)-3, Renderable.SOLID, indices=faces, normal=normals))


