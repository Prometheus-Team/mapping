import cv2 as cv

class Picture:

	def __init__(self, img):
		self.rgb = img
		self.hsv = cv.cvtColor(img, cv.COLOR_RGB2HSV)
		self.depth = None

	def getRGBAt(self, point):
		return self.image[point[1]][point[0]]

	def getDepthAt(self, point):
		return self.depth[point[1]][point[0]]

	def getMultiHSVAt(self, points):
		return self.hsv[points]

	def getHSVAt(self, point):
		return self.hsv[point[0]][point[1]]

	def getWidth(self):
		return self.rgb.shape[1]

	def getHeight(self):
		return self.rgb.shape[0]

	def getShape(self):
		return self.rgb.shape[:2]

