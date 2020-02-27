import numpy as np
import time

def NP(function, array):
	lst = []
	for i in array:
		lst.append(function(i))
	return np.array(lst)

def Between(x, x1, x2):
	return x >= x1 and x <= x2

def Clamp(x, minx, maxx):
	return min(maxx, max(minx, x))

def btcnt(name):
	if name in globals():
		globals()[name][2] = time.time()
	else:
		globals()[name] = [0, 0, time.time()]

def etcnt(name):
	globals()[name][0] += time.time() - globals()[name][2]
	globals()[name][1] += 1

def ptcnt(name):
	print(name, globals()[name][1], globals()[name][0])

def cnt(name):
	if name in globals():
		globals()[name] += 1
	else:
		globals()[name] = 1

def pcnt(name):
	print(name, globals()[name])