from object_models import Object
from object_models import Box
import random
import numpy as np
from utility import custom_math as cm


class Sphere(Object):
	def __init__(self, center, radius, material):
		super().__init__(material)
		self.center = center  # center of the sphere
		self.radius = radius  # radius of the sphere

	def intersect(self, r):
		x0, y0, z0 = r.origin
		xd, yd, zd = r.dir
		xc, yc, zc = self.center

		# A = xd**2 + yd**2 + zd**2  # should always be 1 because of normalization, so I won't include it
		B = 2*(xd*x0 - xd*xc + yd*y0 - yd*yc + zd*z0 - zd*zc)
		C = x0**2 - 2*x0*xc + xc**2 + y0**2 - 2*y0*yc + yc**2 + z0**2 - 2*z0*zc + zc**2 - self.radius**2

		discriminant = B**2 - 4*C
		if discriminant == 0:
			intersect_dist = -B / 2
		elif discriminant > 0:
			t0 = (-B - discriminant**0.5) / 2
			t1 = (-B + discriminant**0.5) / 2
			if t0 > 0 and t1 > 0:
				intersect_dist = t0
			elif t0 < 0 and t1 > 0:
				intersect_dist = t1
			else:
				intersect_dist = -1
		else:  # 0 real roots
			return None
		return r.origin + r.dir*intersect_dist if intersect_dist > 0 else None

	def compute_normal(self, object_point, *args, **kwargs):
		return (object_point - self.center) / self.radius

	def get_position(self):
		return self.center

	def get_bounding_box(self):
		x_min, x_max = self.center[0] - self.radius, self.center[0] + self.radius
		y_min, y_max = self.center[1] - self.radius, self.center[1] + self.radius
		z_min, z_max = self.center[2] - self.radius, self.center[2] + self.radius
		return Box([x_min, y_min, z_min], [x_max, y_max, z_max], None)

	def sample_surface(self, shadow_direction, obj_norm, obj_point, light_norm):
		if abs(obj_norm[0]) > abs(obj_norm[1]):
			shadow_e1 = np.array([shadow_direction[2], 0, -shadow_direction[0]])
			shadow_e1 /= (shadow_direction[0]**2 + shadow_direction[2]**2)**0.5
		else:
			shadow_e1 = np.array([0, -shadow_direction[2], shadow_direction[0]])
			shadow_e1 /= (shadow_direction[1]**2 + shadow_direction[2]**2)**0.5
		shadow_e1 /= np.linalg.norm(shadow_e1)
		shadow_e2 = cm.cross_norm(shadow_direction, shadow_e1)

		angle_to_obj = (1 - self.radius**2 / np.dot(light_norm, light_norm))
		rand_angle = np.pi * 2 * random.random()
		rand_val = random.random()
		angle_cos = 1 - rand_val + rand_val * angle_to_obj
		angle_sin = (1 - angle_cos**2)**0.5
		shadow_direction = shadow_e1 * np.cos(rand_angle) * angle_sin + \
						 shadow_e2 * np.sin(rand_angle) * angle_sin + \
						 shadow_direction * angle_cos
		shadow_direction /= np.linalg.norm(shadow_direction)
		# return angle_to_obj in the future for path tracing?
		return shadow_direction
