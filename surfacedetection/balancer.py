import math
import values
from util import *
import numpy as np

class HSVBalancer:

	def __init__(self):
		self.h = BalanceUnit(0, values.balancer.hueThreshold)
		self.s = BalanceUnit(0, values.balancer.saturationThreshold)
		self.v = BalanceUnit(0, values.balancer.valueThreshold)
		self.units = [self.h, self.s, self.v]

		self.cores = np.array((0,0,0))
		self.thresholds = np.array((values.balancer.hueThreshold, values.balancer.saturationThreshold, values.balancer.valueThreshold))
		self.amount = 0

	def setCore(self, pixel):
		for i in range(len(pixel)):
			self.units[i].core = pixel[i]
		self.cores = pixel
		self.amount = 1

	def adapt(self, pixel):
		self.h.adapt(pixel[0])
		self.s.adapt(pixel[1])
		self.v.adapt(pixel[2])

	def isAcceptable(self, pixel):
		return self.h.isAcceptable(pixel[0]) and self.s.isAcceptable(pixel[1]) and self.v.isAcceptable(pixel[2])

	def balance(self, pixel):
		btcnt('iter')
		acceptable = self.isAcceptable(pixel)
		if acceptable:
			self.adapt(pixel)
		etcnt('iter')
		return acceptable

	def multiBalance(self, pixels):
		btcnt('iter')
		# print("Pixels:",pixels)
		diff = pixels - self.cores
		adaptable = np.logical_and(-self.thresholds <= diff, diff <=  self.thresholds)
		adaptable = np.all(adaptable, axis = 1)
		self.amount += adaptable.size
		adaptableMask = np.tile(adaptable.reshape(adaptable.size, 1), 3)
		adaptablePixelsArray = pixels[adaptableMask]	
		# print(adaptablePixelsArray)
		adaptablePixels = adaptablePixelsArray.reshape(int(adaptablePixelsArray.size/3), 3)
		self.cores = ((self.amount - 1)/self.amount) * self.cores + np.average(adaptablePixels, axis=0) / self.amount
		etcnt('iter')
		return adaptable


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
		diff = value - self.core
		return -self.threshold <= diff <= self.threshold


