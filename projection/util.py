
import numpy as np
import pyrr

def pair(x, y):
    return np.array(np.meshgrid(x,y)).T.reshape((-1,2))

def pair3(x, y, z):
	t = np.array(np.meshgrid(x,y,z)).T
	return t.reshape(int(t.size/3),3)

def cube(resolution):
	lin = np.linspace(-1,1,resolution)
	verts = pair3(lin, lin, lin).astype(dtype=np.float32)
	return verts

def transform(points, matrix):
	return np.append(points, np.ones((points.shape[0], 1)), axis=1).dot(matrix)[:,0:3]

def translate(points, vector):
	return transform(points, pyrr.Matrix44.from_translation(vector))

def rotate(points, angles):
	return transform(points, pyrr.Matrix44.from_eulers(angles))

def normalize(directions):
	return directions/np.sum(np.abs(directions), axis=-1)[...,np.newaxis]
