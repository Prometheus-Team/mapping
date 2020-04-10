
import numpy as np
import pyrr

def pair(x, y):
    return np.array(np.meshgrid(x,y)).T.reshape((-1,2))

def pair3(x, y, z):
	grid = np.meshgrid(z,x,y)
	propergrid = [grid[2], grid[0], grid[1]]
	t = np.array(propergrid).T
	t = t.reshape((-1,3))

	return t

def cube(resolution):
	lin = np.linspace(-1,1,resolution)
	verts = pair3(lin, lin, lin).astype(dtype=np.float32)
	verts = verts.reshape((resolution, resolution, resolution, 3))
	return verts

def transform(points, matrix):
	return np.append(points, np.ones((points.shape[0], 1)), axis=1).dot(matrix)[:,0:3]

def translate(points, vector):
	return transform(points, matrixT(vector))

def matrixT(vector):
	return pyrr.Matrix44.from_translation(vector)
	
def matrixR(angles):
	angles = np.radians(angles)
	return pyrr.Matrix44.from_x_rotation(angles[0]) * pyrr.Matrix44.from_y_rotation(angles[1]) * pyrr.Matrix44.from_z_rotation(angles[2])

def matrixTR(vector, angles):
	return matrixT(vector) * matrixR(angles)

def rotate(points, angles):
	return transform(points, matrixR(angles))

def bounds(points):
	extremePoints = points.reshape((-1,3))
	maxBound = np.nanmax(extremePoints, axis = 0)
	minBound = np.nanmin(extremePoints, axis = 0)
	return minBound, maxBound


