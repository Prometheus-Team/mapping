
import numpy as np
import time

from previewer import *
from normalestimator import *

class R:

	dotThreshold = 0.5

class Decimator:

	def __init__(self):
		pass

	def collapse(self, verts, faces, normals):

		# print(normals)

		nverts = verts.copy()
		exclusiveFaces = self.getExclusiveFaces(verts, faces)
		# exclusiveFaces = self.getMultiExclusiveFaces(faces)

		faceNormals = normals[exclusiveFaces]
		dots = np.sum(np.product(faceNormals, axis=1), axis=1)
		# print(dots)
		collapseCondition = dots > R.dotThreshold

		collapsibleFaces = exclusiveFaces[collapseCondition]
		vertAverages = np.sum(verts[collapsibleFaces], axis=1)/3
		nverts[collapsibleFaces[:,0]] = vertAverages
		nverts[collapsibleFaces[:,1:3]] = np.nan

		index = np.full(np.max(faces) + 1, -1)
		index[collapsibleFaces[:,1]] = collapsibleFaces[:,0]
		index[collapsibleFaces[:,2]] = collapsibleFaces[:,0]
		mask = np.isin(faces, collapsibleFaces[:,1:3])
		translated = index[faces]
		nfaces = np.where(mask, translated, faces)

		nfaces = self.cleanRedundancies(nfaces)

		nverts, nfaces = self.removeNans(nverts, nfaces)

		normals = NormalEstimator.getMeshNormals(nverts, nfaces)

		print("Collapsed " + str(faces.shape[0] - nfaces.shape[0]) + " faces, " + str(verts.shape[0] - nverts.shape[0]) + " vertices")

		return nverts, nfaces, normals

	def cleanRedundancies(self, faces):
		redundancies = np.any(np.array((faces[:,0]  == faces[:,1], faces[:,1] == faces[:,2], faces[:,2] == faces[:,0])).T, axis=1)
		return faces[np.logical_not(redundancies)]

	def removeNans(self, verts, faces):

		index = np.arange(verts.shape[0])
		nonNanIndex = index[np.logical_not(np.isnan(verts[:,0]))]

		lookupIndex = index.copy()
		lookupIndex[nonNanIndex] = index[:nonNanIndex.shape[0]]

		verts = verts[np.logical_not(np.isnan(verts))].reshape(-1,3)
		faces = lookupIndex[faces]

		return verts, faces

	def getExclusiveFaces(self, verts, faces):

		faces = faces.copy()
		used = np.full(verts.shape[0] + 1, False)

		for i in range(faces.shape[0]):
			if (np.any(used[faces[i]])):
				faces[i] = -1
			else:
				used[faces[i]] = True

		return faces[faces >= 0].reshape(-1,3)


	def getMultiExclusiveFaces(self, faces):

		ind1 = np.unique(faces[:,0], return_index=True)[1]
		ind2 = np.unique(faces[:,1], return_index=True)[1]
		ind3 = np.unique(faces[:,2], return_index=True)[1]

		ind = np.intersect1d(np.intersect1d(ind1, ind2), ind3)
		nfaces = faces[ind]

		nf1 = nfaces[np.logical_not(np.isin(nfaces[:,0], nfaces[:,1]))]
		nf2 = nf1[np.logical_not(np.isin(nf1[:,1], nf1[:,2]))]
		nf3 = nf2[np.logical_not(np.isin(nf2[:,2], nf2[:,0]))]

		return nf3
		# condition = np.logical_not(np.any(np.logical_or(faces[0,0] == faces, faces[0,1] == faces, faces[0,2] == faces),axis=1))
		# faces = faces[condition]


if __name__=='__main__':

	m = ModelPreview()
	d = Decimator()

	# m.start()

	verts = np.genfromtxt('../testdata/blobverts.csv')
	faces = np.genfromtxt('../testdata/blobfaces.csv').astype(np.int32)
	normals = np.genfromtxt('../testdata/blobnormals.csv')

	# faces = d.cleanRedundancies(faces)
	# verts = np.genfromtxt('../testdata/collapseverts.csv')
	# faces = np.genfromtxt('../testdata/collapsefaces.csv').astype(np.int32)
	normals = NormalEstimator.getMeshNormals(verts, faces)

	print(faces)
	verts, faces, normals = d.collapse(verts, faces, normals)
	verts, faces, normals = d.collapse(verts, faces, normals)
	verts, faces, normals = d.collapse(verts, faces, normals)

	# faces = d.getExclusiveFaces(verts, faces)
	# faces = d.getMultiExclusiveFaces(faces)
	# print(nfaces.size)

	verts = ((verts/100)*6)-3
	normalProjections = verts + normals/10
	normalDraw = np.concatenate((verts, normalProjections), axis=1)

	# nfaces2 = d.getMultiExclusiveFaces(verts, faces)
	# print(nfaces2.size)
	# print(nfaces)
	# m.addRenderable(Renderable(verts, Renderable.POINTS, pointSize=3))
	# m.addRenderable(Renderable(normalDraw, Renderable.WIREFRAME, color=(0.1, 0.6,1)))

	print(faces)
	m.addRenderable(Renderable(verts, Renderable.SOLID, indices=faces, normal=normals))

	time.sleep(2)
	m.start()


