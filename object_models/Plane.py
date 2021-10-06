from object_models import Object


# TODO: not finished yet
class Plane(Object):
	def __init__(self, vertices, material):
		super().__init__(material)
		self.vertices = vertices

	def get_position(self):
		return sum(self.vertices) / 4
