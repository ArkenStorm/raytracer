class Ray:
	def __init__(self, origin, direction, material):
		self.origin = origin
		self.direction = direction
		self.current_material = material

	def jitter(self):
		pass
