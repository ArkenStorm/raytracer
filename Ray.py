class Ray:
	def __init__(self, origin, direction, material):
		self.origin = origin
		self.direction = direction
		self.current_material = material

	def jitter(self, factor):
		# randomly choose between 1 and 3 axes
		# choose number between 1 and -1, include factor somehow
		# make sure to normalize
		pass
