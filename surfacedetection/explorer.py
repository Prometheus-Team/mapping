from surface import Surface


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
		for i in range(10):
			points = self.surface.getExpandablePoints()
			if len(points) == 0:
				break
			self.exploreStep(points)
		#print("After: " + str(self.surface))


	def exploreStep(self, points):
		for i in points:
			#print("Balancing:", i)
			if (self.surface.balancer.balance(self.surface.surfaceSet.picture.getHSVAt(i))):
				#print("AAAAAAAAAAAAADDDDDDDDDDDEEEEEEEEEEEEEDDDDDDDDDDDDDD")
				self.surface.appendPoint(i)




	# def adapt():
	# 	for i in self.surfaceset.surfaces:
	# 		if i.contains(self.location):
	# 			self.surface = i

	
		


