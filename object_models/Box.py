from object_models import Object
import numpy as np


class Box(Object):
	def __init__(self, min_vals, max_vals, material):
		super().__init__(material)
		self.min_vals = min_vals
		self.max_vals = max_vals
		self.axis_aligned = True  # TODO: Make this customizable in the future?

	def intersect(self, r0, rd):
		if self.axis_aligned:
			t_near = -float('inf')
			t_far = float('inf')
			for axis in range(len(r0)):  # TODO: check for direction 0
				t1 = (self.min_vals[axis] - r0[axis]) / rd[axis]
				t2 = (self.max_vals[axis] - r0[axis]) / rd[axis]
				if t1 > t2:
					t1, t2 = t2, t1
				if t1 > t_near:
					t_near = t1
				if t2 < t_far:
					t_far = t2
				if t_near > t_far or t_far < 0:
					return None
			# If ray is inside the box
			if self.max_vals[0] > r0[0] > self.min_vals[0] and \
					self.max_vals[1] > r0[1] > self.min_vals[1] and \
					self.max_vals[2] > r0[2] > self.min_vals[2]:
				return r0 + rd * t_far
			return r0 + rd * t_near if t_near != -float('inf') else None
		else:  # TODO: If non axis-aligned boxes get implemented
			pass

	def compute_normal(self, object_point, *args, **kwargs):  # Only works for axis-aligned right now
		normal = [(self.min_vals[0] - self.max_vals[0]), 0, 0]
		minimum = abs(object_point[0] - self.min_vals[0])
		temp = abs(object_point[0] - self.max_vals[0])
		if temp < minimum:
			minimum = temp
			normal = [self.max_vals[0] - self.min_vals[0], 0, 0]
		temp = abs(object_point[1] - self.max_vals[1])
		if temp < minimum:
			minimum = temp
			normal = [0, self.max_vals[1] - self.min_vals[1], 0]
		temp = abs(object_point[1] - self.min_vals[1])
		if temp < minimum:
			minimum = temp
			normal = [0, self.min_vals[1] - self.max_vals[1], 0]
		temp = abs(object_point[2] - self.min_vals[2])
		if temp < minimum:
			minimum = temp
			normal = [0, 0, self.min_vals[0] - self.max_vals[0]]
		temp = abs(object_point[2] - self.max_vals[2])
		if temp < minimum:
			normal = [0, 0, self.max_vals[0] - self.min_vals[0]]

		normal = np.array(normal)
		return normal / np.linalg.norm(normal)

	def get_position(self):
		# TODO: not quite sure how to check a box area light yet
		pass

	def get_bounding_box(self):
		return self
