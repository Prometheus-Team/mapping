
import numpy as np


class NormalEstimator:

	def getEstimatedNormals(points):
		infinitum = (1e6, 1e6, 1e6)
		infinitumThreshold = 1e3

		#shift points right, left, down, up
		rollr = np.roll(points, 1, axis=1)
		rollr[:,0] = infinitum

		rolll = np.roll(points, -1, axis=1)
		rolll[:,-1] = infinitum

		rolld = np.roll(points, 1, axis=0)
		rolld[0,:] = infinitum

		rollu = np.roll(points, -1, axis=0)
		rollu[-1,:] = infinitum

		#find the differences
		diffr = rollr - points
		diffl = rolll - points
		diffu = rollu - points
		diffd = rolld - points

		#cross product differences to find normals
		crossrd = np.cross(diffr, diffd)
		crosslu = np.cross(diffl, diffu)

		#average the two normals
		normals = NormalEstimator.normalize(crosslu + crossrd)

		#set border normals to zero
		normals[np.sum((np.abs(diffr), np.abs(diffl), np.abs(diffu), np.abs(diffd)), axis=0) > infinitumThreshold] = 0


		return normals

	
	def normalize(directions):
		return directions/np.sum(np.abs(directions), axis=-1)[...,np.newaxis]