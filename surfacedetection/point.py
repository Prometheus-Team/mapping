

class Point:
	x = 0
	y = 0

	def __init__(self, x, y):
		self.x = x
		self.y = y


	def __str__(self):
		return str((self.x, self.y))

	def __eq__(self, point):
		return isinstance(point, Point) and self.x == point.x and self.y == point.y

	def __ne__(self, point):
		return not self == point

	def __getitem__(self, key):
		if key == 0:
			return self.x
		elif key == 1:
			return self.y

