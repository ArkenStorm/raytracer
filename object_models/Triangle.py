from object_models.Object import Object
import numpy as np
import custom_math as cm


class Triangle(Object):
	def __init__(self, vertices, kd, ks, ka, od, os, kgls):
		super().__init__(kd, ks, ka, od, os, kgls)
		self.vertices = vertices  # list of vertices to render
		self.normal = self.compute_normal()

	def intersect(self, r0, rd):
		normal = self.normal.copy()
		preemptive_test = np.dot(normal, rd)
		if preemptive_test == 0:  # ray is parallel, does not intersect
			return None
		if preemptive_test > 0:
			normal = -normal
			preemptive_test = np.dot(normal, rd)
		plane_dist = -np.dot(normal, self.vertices[0])
		triangle_point_dist = -(np.dot(normal, r0) + plane_dist) / preemptive_test
		if triangle_point_dist <= 0:
			return None
		intersect_point = r0 + rd*triangle_point_dist
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
