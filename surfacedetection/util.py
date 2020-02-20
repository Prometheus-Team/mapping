
def Between(x, x1, x2):
	return x >= x1 and x <= x2

def Clamp(x, minx, maxx):
	return min(maxx, max(minx, x))

def cnt(name):
	if name in globals():
		globals()[name] += 1
	else:
		globals()[name] = 1

def pcnt(name):
	print(name, globals()[name])