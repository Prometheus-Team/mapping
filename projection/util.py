
import numpy as np

def pair(x, y):
    return np.array(np.meshgrid(x,y)).T.reshape((-1,2))

def pair3(x, y, z):
	t = np.array(np.meshgrid(x,y,z)).T
	return t.reshape(int(t.size/3),3)

def cube(resolution):
	lin = np.linspace(-1,1,resolution)
	verts = pair3(lin, lin, lin).astype(dtype=np.float32)
	return verts

