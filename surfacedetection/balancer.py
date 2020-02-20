import math
import values


class HSVBalancer:

	def __init__(self):
		self.h = BalanceUnit(0, values.balancer.hueThreshold)
		self.s = BalanceUnit(0, values.balancer.saturationThreshold)
		self.v = BalanceUnit(0, values.balancer.valueThreshold)
		self.units = [self.h, self.s, self.v]

	def setCore(self, pixel):
		for i in range(len(pixel)):
			self.units[i].core = pixel[i]

	def adapt(self, pixel):
		self.h.adapt(pixel[0])
		self.s.adapt(pixel[1])
		self.v.adapt(pixel[2])

	def isAcceptable(self, pixel):
		return self.h.isAcceptable(pixel[0]) and self.s.isAcceptable(pixel[1]) and self.v.isAcceptable(pixel[2])

	def balance(self, pixel):
		if (self.isAcceptable(pixel)):
			self.adapt(pixel)
			return True

		return False


#use of acceptance factors: each balance units has an acceptance factor that the difference will be multiplied by. The 
#pixel is rejected if the total combined acceptance of all units exceeds a threshold

class BalanceUnit:

	def __init__(self, core, threshold):
		self.core = core
		self.threshold = threshold
		self.amount = 0

	def adapt(self, value):
		self.amount += 1
		self.core = ((self.amount - 1)/self.amount)*self.core + value/self.amount

	def isAcceptable(self, value):
		diff = math.fabs(value - self.core)/255
		return diff <= self.threshold


