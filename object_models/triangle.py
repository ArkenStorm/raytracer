from object_models import Object
from object_models import Box
import random
import numpy as np
from utility import custom_math as cm


class Triangle(Object):
	def __init__(self, vertices, material, texture=None):
		super().__init__(material, texture)
		self.vertices = vertices  # list of vertices to render
		self.normal = self.compute_normal()

	def intersect(self, r):
		normal = self.normal.copy()
		preemptive_test = np.dot(normal, r.dir)
		if preemptive_test == 0:  # ray is parallel, does not intersect
			return None
		if preemptive_test > 0:
			normal = -normal
			preemptive_test = np.dot(normal, r.dir)
		plane_dist = -np.dot(normal, self.vertices[0])
		triangle_point_dist = -(np.dot(normal, r.origin) + plane_dist) / preemptive_test
		if triangle_point_dist <= 0:
			return None
		intersect_point = r.origin + r.dir*triangle_point_dist
		normal = -normal  # only flip it for the first part of the intersection algorithm

		sign_total = 0
		C = cm.cross_norm(self.vertices[1] - self.vertices[0], intersect_point - self.vertices[0], False)
		sign_total += -1 if np.dot(normal, C) < 0 else 1

		C = cm.cross_norm(self.vertices[2] - self.vertices[1], intersect_point - self.vertices[1], False)
		sign_total += -1 if np.dot(normal, C) < 0 else 1

		C = cm.cross_norm(self.vertices[0] - self.vertices[2], intersect_point - self.vertices[2], False)
		sign_total += -1 if np.dot(normal, C) < 0 else 1

		return intersect_point if abs(sign_total) == 3 else None

	def compute_normal(self, *args, **kwargs):
		v1 = self.vertices[1] - self.vertices[0]
		v2 = self.vertices[2] - self.vertices[0]
		return cm.cross_norm(v1, v2)

	def get_position(self):
		return sum(self.vertices) / 3

	def get_bounding_box(self):
		x_coords = [x[0] for x in self.vertices]
		y_coords = [y[1] for y in self.vertices]
		z_coords = [z[2] for z in self.vertices]
		min_vals = [min(x_coords), min(y_coords), min(z_coords)]
		max_vals = [max(x_coords), max(y_coords), max(z_coords)]
		return Box(min_vals, max_vals, None)

	def sample_surface(self, shadow_direction, obj_point, *args, **kwargs):
		p1 = self.vertices[0] + (self.vertices[1] - self.vertices[0]) * random.random()
		p2 = self.vertices[1] + (self.vertices[2] - self.vertices[0]) * random.random()
		final_point = p1 + (p2 - p1) * random.random()
		shadow_direction = final_point - obj_point
		shadow_direction /= np.linalg.norm(shadow_direction)
		return

	def get_uv(self, point):
		# I have no idea what I'm doing
		a, b, c = self.vertices
		total_area = cm.cross_norm(b - a, c - a)
		area_a = cm.cross_norm(c - b, point - b) / total_area
		area_b = cm.cross_norm(a - c, point - c) / total_area
		area_c = None
		return None
