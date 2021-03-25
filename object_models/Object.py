import numpy as np


class Object:
	def __init__(self, kd, ks, ka, od, os, kgls):
		self.kd = kd  # diffuse coefficient; changed to 1 because example scenes/inputs are different.S
		self.ks = ks  # specular coefficient
		self.ka = ka  # ambient coefficient
		self.od = od  # diffuse reflectance color
		self.os = os  # object specular color
		self.kgls = kgls  # glossy constant
		# add index of refraction/material?
		# add reflectivity constant/boolean?
		# add transparency constant/boolean?

	# returns the intersection point
	def intersect(self, r0, rd):
		pass

	def compute_normal(self, *args, **kwargs):
		return 0

	# pl == point light
	def luminance(self, ambient_color, pl_color, pl_direction, obj_norm, view_direction, light_reflect, in_shadow):
		if in_shadow:
			return np.clip(self.ka * ambient_color * self.od, 0.0, 1.0)

		return np.clip((self.ka * ambient_color * self.od +
			   self.kd * pl_color * self.od * max(0.0, np.dot(obj_norm, pl_direction)) +
			   self.ks * pl_color * self.os * max(0.0, np.dot(view_direction, light_reflect)) ** self.kgls), 0.0, 1.0)
