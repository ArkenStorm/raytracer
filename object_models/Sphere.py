from object_models import Object
from object_models import Box


class Sphere(Object):
	def __init__(self, center, radius, material):
		super().__init__(material)
		self.center = center  # center of the sphere
		self.radius = radius  # radius of the sphere

	def intersect(self, r0, rd):
		x0, y0, z0 = r0
		xd, yd, zd = rd
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
		return r0 + rd*intersect_dist if intersect_dist > 0 else None

	def compute_normal(self, object_point, *args, **kwargs):
		return (object_point - self.center) / self.radius

	def get_position(self):
		return self.center

	def get_bounding_box(self):
		x_min, x_max = self.center[0] - self.radius, self.center[0] + self.radius
		y_min, y_max = self.center[1] - self.radius, self.center[1] + self.radius
		z_min, z_max = self.center[2] - self.radius, self.center[2] + self.radius
		return Box([x_min, y_min, z_min], [x_max, y_max, z_max], None)
