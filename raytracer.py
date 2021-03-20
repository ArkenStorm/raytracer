import numpy as np
from math import radians as rad

image_height = 1000
image_width = 1000
epsilon = 0.0000001
i_min, j_min = 0, 0
i_max, j_max = image_height - 1, image_width - 1
num_reflections = 4  # max ray tree depth
min_light_val = 0.05  # ????
objects = []
camera_look_at = (None, None, None)  # vector list of x/y/z
camera_look_from = (None, None, None)
camera_look_up = (None, None, None)

u, v, w = (None, None, None), (None, None, None), (None, None, None)
u_max, u_min = -1, -1
v_max, v_min = -1, -1

field_of_view = 0
light_direction = None
light_color = None
ambient_light = None
background_color = None
scene_info = open("scenes/custom.rayTracing")
scene_name = "custom.ppm"
render = [[0 for i in range(image_width)] for j in range(image_height)]

# num_crossings logic; debug eventually; general polygonal intersection
		# dominant_index = np.argmax(normal)
		# proj_vertices = []
		# proj_point = np.delete(r0, dominant_index)
		# for vertex in self.vertices:
		# 	proj_vertices.append(np.delete(vertex, dominant_index) - proj_point)
		# num_crossings = 0
		# sign_holder = -1 if proj_vertices[0][1] < 0 else 1
		# for i, vertex in enumerate(proj_vertices):
		# 	next_i = (i + 1) % len(proj_vertices)
		# 	next_sign_holder = -1 if proj_vertices[next_i][1] < 0 else 1
		# 	if sign_holder != next_sign_holder:
		# 		if proj_vertices[i][0] > 0 and proj_vertices[next_i][0]:
		# 			num_crossings += 1
		# 		elif proj_vertices[i][0] > 0 or proj_vertices[next_i][0]:
		# 			u_cross = proj_vertices[i][0] - proj_vertices[i][1] * (proj_vertices[next_i][0] - proj_vertices[i][0]) / (proj_vertices[next_i][1] - proj_vertices[i][1])
		# 			if u_cross > 0:
		# 				num_crossings += 1
		# 	sign_holder = next_sign_holder
		# return intersect_point if num_crossings % 2 == 1 else None


class Object:
	def __init__(self, kd, ks, ka, od, os, kgls):
		self.kd = kd  # diffuse coefficient; changed to 1 because example scenes/inputs are different.S
		self.ks = ks  # specular coefficient
		self.ka = ka  # ambient coefficient
		self.od = od  # diffuse reflectance color
		self.os = os  # object specular color
		self.kgls = kgls  # glossy constant
		# add index of refraction/material?

	# returns the intersection point
	def intersect(self, r0, rd):
		pass

	def compute_normal(self, object_point):
		return 0

	# pl == point light
	def luminance(self, ambient_color, pl_color, pl_direction, obj_norm, view_direction, light_reflect, inShadow):
		if inShadow:
			return np.clip(self.ka * ambient_color * self.od, 0.0, 1.0)

		return np.clip((self.ka * ambient_color * self.od +
			   self.kd * pl_color * self.od * max(0.0, np.dot(obj_norm, pl_direction)) +
			   self.ks * pl_color * self.os * max(0.0, np.dot(view_direction, light_reflect)) ** self.kgls), 0.0, 1.0)


class Sphere(Object):
	def __init__(self, center, radius, kd, ks, ka, od, os, kgls):
		super().__init__(kd, ks, ka, od, os, kgls)
		self.center = center  # center of the sphere
		self.radius = radius  # radius of the sphere

	def intersect(self, r0, rd):
		x0, y0, z0 = r0
		xd, yd, zd = rd
		xc, yc, zc = self.center

		A = xd**2 + yd**2 + zd**2
		B = 2*(xd*x0 - xd*xc + yd*y0 - yd*yc + zd*z0 - zd*zc)
		C = x0**2 - 2*x0*xc + xc**2 + y0**2 - 2*y0*yc + yc**2 + z0**2 - 2*z0*zc + zc**2 - self.radius**2

		discriminant = B**2 - 4*C
		t0, t1, intersect_dist = None, None, None
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

	def compute_normal(self, object_point):
		return (object_point - self.center) / self.radius


class Triangle(Object):
	def __init__(self, vertices, kd, ks, ka, od, os, kgls):
		super().__init__(kd, ks, ka, od, os, kgls)
		self.vertices = vertices  # list of vertices to render
		# compute normal once and store it
		self.normal = self.compute_normal(None)

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
		C = cross_norm(self.vertices[1] - self.vertices[0], intersect_point - self.vertices[0], False)
		sign_total += -1 if np.dot(normal, C) < 0 else 1

		C = cross_norm(self.vertices[2] - self.vertices[1], intersect_point - self.vertices[1], False)
		sign_total += -1 if np.dot(normal, C) < 0 else 1

		C = cross_norm(self.vertices[0] - self.vertices[2], intersect_point - self.vertices[2], False)
		sign_total += -1 if np.dot(normal, C) < 0 else 1

		return intersect_point if abs(sign_total) == 3 else None

	def compute_normal(self, object_point):
		v1 = self.vertices[1] - self.vertices[0]
		v2 = self.vertices[2] - self.vertices[0]
		return cross_norm(v1, v2)


def parse_scene_info():
	global objects, camera_look_at, camera_look_from, camera_look_up, field_of_view, light_direction
	global light_color, ambient_light, background_color, u, v, w, u_max, u_min, v_max, v_min

	camera_look_at = np.array(list(map(float,scene_info.readline().split()[1:])))
	camera_look_from = np.array(list(map(float,scene_info.readline().split()[1:])))
	camera_look_up = np.array(list(map(float,scene_info.readline().split()[1:])))
	field_of_view = 2 * float(scene_info.readline().split()[1])  # example scenes give pre-halved FoV

	light_info = scene_info.readline().split()
	light_direction, light_color = np.array(list(map(float, light_info[1:4]))), np.array(list(map(float, light_info[5:])))

	ambient_light = np.array(list(map(float, scene_info.readline().split()[1:])))
	background_color = np.array(list(map(float, scene_info.readline().split()[1:])))

	while line := scene_info.readline().split():
		if line[0].lower() == "sphere":
			center = (x, y, z) = list(map(float, line[2:5]))
			radius = float(line[6])
			kd = float(line[8])
			ks = float(line[10])
			ka = float(line[12])
			od = np.array(list(map(float, line[14:17])))
			os = np.array(list(map(float, line[18:21])))
			kgls = int(line[22])  # kgls always int?

			objects.append(Sphere(center, radius, kd, ks, ka, od, os, kgls))
		elif line[0].lower() == "triangle":
			vertices = [np.array(list(map(float, line[1:4]))), np.array(list(map(float, line[4:7]))),
						np.array(list(map(float, line[7:10])))]
			kd = float(line[11])
			ks = float(line[13])
			ka = float(line[15])
			od = np.array(list(map(float, line[17:20])))
			os = np.array(list(map(float, line[21:24])))
			kgls = int(line[25])

			objects.append(Triangle(vertices, kd, ks, ka, od, os, kgls))
		else:
			pass  # render other polygons eventually

	w = (camera_look_from - camera_look_at) / np.linalg.norm(camera_look_from - camera_look_at)
	u = cross_norm(camera_look_up, w)
	v = cross_norm(w, u)
	u_max = np.tan(rad(field_of_view / 2)) * np.linalg.norm(camera_look_at - camera_look_from)
	u_min = -u_max
	v_max = np.tan(rad(field_of_view / 2)) * np.linalg.norm(camera_look_at - camera_look_from)
	v_min = -v_max


def compute_primary_ray(i, j):  # i, j are viewport points
	global u, v, w, u_max, u_min, v_max, v_min, i_max, i_min, j_max, j_min, camera_look_at, camera_look_from
	ray_u = (i - i_min) * ((u_max - u_min) / (i_max - i_min)) + u_min
	ray_v = (j - j_min) * ((v_max - v_min) / (j_max - j_min)) + v_min
	ray_w = 0
	ux, uy, uz = u
	vx, vy, vz = v
	wx, wy, wz = w
	look_at_x, look_at_y, look_at_z = camera_look_at
	screen_to_world = np.array([
		[ux, uy, uz, 0],
		[vx, vy, vz, 0],
		[wx, wy, wz, 0],
		[0, 0, 0, 1]
	])
	translate = np.array([
		[1, 0, 0, -look_at_x],  # make them positive?
		[0, 1, 0, -look_at_y],
		[0, 0, 1, -look_at_z],
		[0, 0, 0, 1]
	])
	ray_screen = np.array([ray_u, ray_v, ray_w]) - camera_look_from
	ray_screen = ray_screen / np.linalg.norm(ray_screen)
	ray_screen = np.append(ray_screen, 1)
	return screen_to_world@translate@ray_screen  # ray in world space


def is_in_shadow(point):
	global light_direction, epsilon
	shadow_direction = light_direction - point
	shadow_direction = shadow_direction / np.linalg.norm(shadow_direction)
	# ignore shadow_color/obj from this, it doesn't matter
	shadow_color, shadow_intersect, shadow_obj = compute_intersections(point + epsilon * shadow_direction,
																	   shadow_direction, 0)
	return True if shadow_intersect is not None else False


# r0 == ray origin, rd == ray direction;
def compute_intersections(r0, rd, spawn_depth):
	global objects, ambient_light, light_color, light_direction, epsilon

	min_dist = float('inf')
	intersect_point = None
	intersect_obj = None
	illumination = np.array([0.0, 0.0, 0.0])
	for obj in objects:
		point = obj.intersect(r0, rd)
		if point is not None:
			distance = distance_3D(r0, point)
			if distance < min_dist:
				min_dist = distance
				intersect_point = point
				intersect_obj = obj
	if intersect_point is None:
		return None, None, None  # no intersection

	object_norm = intersect_obj.compute_normal(intersect_point)
	reflect_direction = rd - 2 * object_norm * (np.dot(rd, object_norm))
	light_vector = light_direction - 2 * object_norm * (np.dot(light_direction, object_norm))
	light_reflection = light_vector / np.linalg.norm(light_vector)

	obj_luminance = intersect_obj.luminance(ambient_light, light_color, light_direction,
											object_norm, rd, light_reflection, is_in_shadow(intersect_point))
	illumination = np.clip(illumination + obj_luminance, 0.0, 1.0)  # obj_luminance should never be None

	if intersect_obj.ks > 0 and spawn_depth > 0:
		# calculate and trace reflection/transmission ray (whether reflective or transparent surface)
		reflect_point = intersect_point + epsilon * reflect_direction
		recursive_color, recursive_intersect, recursive_obj = compute_intersections(reflect_point,
																					reflect_direction, spawn_depth - 1)
		if recursive_color is not None:
			illumination = np.clip(illumination + recursive_color * intersect_obj.ks, 0.0, 1.0)
		else:
			illumination = np.clip(illumination + background_color * intersect_obj.ks, 0.0, 1.0)

	return illumination, intersect_point, intersect_obj


def cross_norm(a, b, normalize=True):
	ax, ay, az = a
	bx, by, bz = b

	cx = ay * bz - az * by
	cy = az * bx - ax * bz
	cz = ax * by - ay * bx

	norm = (cx * cx + cy * cy + cz * cz)**0.5
	return np.array([cx / norm, cy / norm, cz / norm]) if normalize else np.array([cx, cy, cz])


def distance_2D(a, b):
	x1, y1 = a
	x2, y2 = b
	return ((x2-x1)**2)+((y2-y1)**2)**0.5


# find the distance between two 3D points
def distance_3D(a, b):
	x1, y1, z1 = a
	x2, y2, z2 = b
	return (((x2-x1)**2)+((y2-y1)**2)+((z2-z1)**2))**(1/2)


def write_to_ppm():
	global image_height, image_width, scene_name, render
	ppm_file = open(scene_name, "w+")

	ppm_file.write(f'P3\n{image_width} {image_height}\n255\n')
	for j in range(image_height - 1, -1, -1):
		write_line = ""
		for i in range(image_width):
			r, g, b = render[i][j]  # RGB tuples stored in the render array
			write_line += f'{r * 255} {g * 255} {b * 255} '  # multiply values by 255 for ppm?
		ppm_file.write(write_line)
	print("All rows written")

	ppm_file.close()


parse_scene_info()
for i in range(image_height):
	for j in range(image_width):
		ray = compute_primary_ray(i, j)[:3]
		color, intersect_point, intersect_object = compute_intersections(camera_look_from, ray, num_reflections)
		pixel_color = color if color is not None else background_color
		render[i][j] = pixel_color

write_to_ppm()
