import numpy as np


class Object:
	def __init__(self, material):
		self.material = material

	# returns the intersection point
	def intersect(self, r):
		pass

	def compute_normal(self, *args, **kwargs):
		return 0

	def get_position(self):
		return 0

	def get_bounding_box(self):
		return None

	# pl == point light
	def luminance(self, ambient_color, pl_color, pl_direction, obj_norm, view_direction, light_reflect, in_shadow):
		if in_shadow:
			return np.clip(self.material.ka * ambient_color * self.material.od, 0.0, 1.0)

		return np.clip((self.material.ka * ambient_color * self.material.od +
			   self.material.kd * pl_color * self.material.od * max(0.0, np.dot(obj_norm, pl_direction)) +
			   self.material.ks * pl_color * self.material.os * max(0.0, np.dot(view_direction, light_reflect)) ** self.material.kgls), 0.0, 1.0)

	# Area light sampling
	def sample_surface(self, shadow_ray, obj_norm, obj_point, light_norm):
		pass

	# TODO: UV mapping stuff
	def get_uv(self):
		pass
