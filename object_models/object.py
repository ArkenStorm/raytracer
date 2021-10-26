import numpy as np


class Object:
	def __init__(self, material, texture=None):
		self.material = material
		self.texture = texture

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
	def luminance(self, ambient_color, pl_color, pl_direction, point, norm, view_direction, light_reflect, in_shadow):
		if self.texture is not None:
			u, v = self.get_uv(point)
			uv_color = self.texture.get_color(u, v)
			ambient = ambient_color * uv_color
			diffuse = pl_color * uv_color
			illumination = diffuse
		else:
			ambient = self.material.ka * ambient_color * self.material.od
			diffuse = self.material.kd * pl_color * self.material.od * max(0.0, np.dot(norm, pl_direction))
			specular = self.material.ks * pl_color * self.material.os * max(0.0, np.dot(view_direction, light_reflect)) ** self.material.kgls
			illumination = ambient + diffuse + specular

		if in_shadow:
			return np.clip(ambient, 0.0, 1.0)

		return np.clip(illumination, 0.0, 1.0)

	# Area light sampling
	def sample_surface(self, *args, **kwargs):
		pass

	def get_uv(self, point):
		return None, None
