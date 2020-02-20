
class Color:

	def Make(array):

		if len(array) > 4:
			raise Exception("Too many inputs for Color.Make")

		alpha = array[3] if len(array) > 3 else 1
		color = Color(array[0], array[1], array[2], alpha)


	def __init__(self, r, g, b, a):
		self.r = r
		self.g = g
		self.b = b
		self.a = a


