import random
import numpy as np


class Ray:
	def __init__(self, origin, direction, material):
		self.origin = origin
		self.dir = direction
		self.current_material = material

	def jitter(self, factor):
		jitter_axes = random.sample([0,1,2], k=random.randint(0,3))
		for i in jitter_axes:
			self.dir[i] += (random.uniform(-.1, .1) * (1/factor))  # tweak how factor applies?
		self.dir /= np.linalg.norm(self.dir)
		return self
