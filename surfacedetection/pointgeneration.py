from point import *
from util import *
import random
import matplotlib.pyplot as plt

class PointGeneration:

	def generateRandomPoints(width, height, amount):
		points = []
		for i in range(amount):
			points.append(Point(random.randrange(0, width), random.randrange(0, height)))
		return points

	def generateUniformPoints(width, height, amount):
		points = []
		space = PointGeneration.getSpacing(width, height, amount)
		for i in range(int(width/space)):
			for j in range(int(height/space)):
				points.append(Point(i*space, j*space))

		return points

	def generateRandomizedUniformPoints(width, height, amount, varianceFactor):
		points = PointGeneration.generateUniformPoints(width, height, amount)
		variance = PointGeneration.getSpacing(width, height, amount) * varianceFactor

		for i in points:
			i.x += (random.random() * variance) - variance/2;
			i.y += (random.random() * variance) - variance/2;
			i.x = int(Clamp(i.x, 0, width-1))
			i.y = int(Clamp(i.y, 0, height-1))

		return points

	def getSpacing(width, height, amount):
		return ((width*height)/amount)**0.5;


#tests

# x,y = [],[]

# for i in PointGeneration.generateRandomizedUniformPoints(100,100, 500, 1):
# 	x.append(i.x)
# 	y.append(i.y)


# plt.scatter(x=x, y=y, c='r', s=5)

# plt.show()

