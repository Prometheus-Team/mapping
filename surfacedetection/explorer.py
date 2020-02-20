from surface import Surface
import numpy as np
from util import *

class Explorer:

	def __init__(self, location, surfaceset):
		self.location = location
		self.surfaceSet = surfaceset
		self.surface = None

		#remove because dynamic cores might change rejected status
		self.rejectedPoints = []

	def isOnSurface(self):
		for i in self.surfaceSet.surfaces:
			if i.contains(self.location):
				return True

		return False

	def declareSurface(self):
		self.surface = self.surfaceSet.createSurface()
		self.surface.appendPoint(self.location)
		self.surface.balancer.setCore(self.surface.surfaceSet.picture.getHSVAt(self.location))

	def explore(self):
		#print("Before: " + str(self.surface))
		# print("Expandables:", [str(i) for i in points])
		for i in range(30):
			points = self.surface.getExpandablePoints()
			if len(points) == 0:
				break
			self.exploreMultiStep(points)
		#print("After: " + str(self.surface))


	def exploreStep(self, points):
		for i in points:
			if i in self.rejectedPoints:
				continue
			#print("Balancing:", i)
			if (self.surface.balancer.balance(self.surface.surfaceSet.picture.getHSVAt(i))):
				#print("AAAAAAAAAAAAADDDDDDDDDDDEEEEEEEEEEEEEDDDDDDDDDDDDDD")
				self.surface.appendPoint(i)
			else:
				self.rejectedPoints.append(i)

	def exploreMultiStep(self, points):
		pixels = np.array([self.surface.surfaceSet.picture.getHSVAt(i) for i in points])
		adaptable = self.surface.balancer.multiBalance(pixels)
		for i in range(len(points)):
			if adaptable[i]:
				self.surface.appendPoint(points[i])




	# def adapt():
	# 	for i in self.surfaceset.surfaces:
	# 		if i.contains(self.location):
	# 			self.surface = i

	
		


