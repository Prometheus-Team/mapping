from surface import Surface
import numpy as np
from util import *

class Explorer:

	spots = []

	def initializeSpots(width, height):
		Explorer.spots = np.zeros((width, height))


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
			btcnt('bttl')
			points = self.surface.getExpandablePoints()
			etcnt('bttl')
			# points = self.surface.getMultiExpandablePoints()
			# print("Singu:",spoints)
			# print("Multi:",points)
			if len(points) == 0:
				break
			#self.exploreStep(points)
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
		# print("Multistep Points:", points)
		pixels = self.surface.surfaceSet.picture.getMultiHSVAt(points)
		# print("Pixels:", pixels)
		adaptable = self.surface.balancer.multiBalance(pixels)
		# print("Adaptable:", adaptable)
		for i in range(len(points[0])):
			if adaptable[i]:
				self.surface.appendPoint((points[0][i], points[1][i]))




	# def adapt():
	# 	for i in self.surfaceset.surfaces:
	# 		if i.contains(self.location):
	# 			self.surface = i

	
		


