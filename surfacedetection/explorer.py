from surface import Surface
import numpy as np
from util import *

class Explorer:


	def __init__(self, location, surfaceset):
		self.location = location
		self.surfaceSet = surfaceset
		self.surface = None
		self.lCoverage = -1
		self.completed = False
		#remove because dynamic cores might change rejected status
		self.rejectedPoints = []

	def reset(self):
		self.lCoverage = -1
		self.completed = False

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

		if self.completed:
			return

		# btcnt('bttl')
		points = self.surface.getExpandablePoints()
		# etcnt('bttl')
		if len(points) == 0:
			# print("Complete",self.surface.color,"because no more expandable points")
			self.completed = True
			return
		self.exploreMultiStep(points)
		coverage = self.surface.getCoverage()
		if (coverage == self.lCoverage):
			# print("Complete",self.surface.color,"because coverage",coverage,"reached,",self.surface.balancer.cores)
			self.completed = True
		self.lCoverage = coverage

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

		#just add adaptable mask to surface mask
		# btcnt('bttl')
		for i in range(len(points[0])):
			if adaptable[i]:
				self.surface.appendPoint((points[0][i], points[1][i]))
		# etcnt('bttl')





	# def adapt():
	# 	for i in self.surfaceset.surfaces:
	# 		if i.contains(self.location):
	# 			self.surface = i

	
		


