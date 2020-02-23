import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

x = np.zeros((5,5), dtype=np.int32)
x[4,2] = 1

shift = 1

print(x)

rshift = np.pad(x, ((0,0),(shift,0)))[:,:-shift]
lshift = np.pad(x, ((0,0),(0,shift)))[:,shift:]

hshift = np.maximum(np.maximum(rshift, lshift), x)

print(hshift)

dshift = np.pad(hshift, ((shift, 0), (0, 0)))[:-shift,:]
ushift = np.pad(hshift, ((0,shift),(0,0)))[shift:,:]

tshift = np.maximum(np.maximum(dshift, ushift), hshift)

print(tshift)