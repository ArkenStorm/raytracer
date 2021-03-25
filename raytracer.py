from object_models import *
from environment import *
import custom_math as cm

image_height = 1000
image_width = 1000
epsilon = 0.0000001
i_min, j_min = 0, 0
i_max, j_max = image_height - 1, image_width - 1
num_reflections = 4  # max ray tree depth
min_light_val = 0.05  # ????
objects = []
camera = None
scene = None

scene_info = open("scenes/custom.rayTracing")
scene_name = "custom.ppm"
render = [[0 for j in range(image_width)] for i in range(image_height)]


def parse_scene_info():
	global objects, camera, scene

	look_at = np.array(list(map(float,scene_info.readline().split()[1:])))
	look_from = np.array(list(map(float,scene_info.readline().split()[1:])))
	look_up = np.array(list(map(float,scene_info.readline().split()[1:])))
	fov = 2 * float(scene_info.readline().split()[1])  # example scenes give pre-halved FoV
	camera = Camera(look_at, look_from, look_up, fov)

	light_info = scene_info.readline().split()
	light_direction, light_color = np.array(list(map(float, light_info[1:4]))), np.array(list(map(float, light_info[5:])))

	ambient_light = np.array(list(map(float, scene_info.readline().split()[1:])))
	background_color = np.array(list(map(float, scene_info.readline().split()[1:])))
	scene = Scene(light_direction, light_color, ambient_light, background_color)

	while line := scene_info.readline().split():
		if line[0].lower() == "sphere":
			center = list(map(float, line[2:5]))
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


def compute_primary_ray(i, j):  # i, j are viewport points
	global i_max, i_min, j_max, j_min, camera
	ray_u = (i - i_min) * ((camera.u_max - camera.u_min) / (i_max - i_min)) + camera.u_min
	ray_v = (j - j_min) * ((camera.v_max - camera.v_min) / (j_max - j_min)) + camera.v_min
	ray_w = 0
	ux, uy, uz = camera.u
	vx, vy, vz = camera.v
	wx, wy, wz = camera.w
	look_at_x, look_at_y, look_at_z = camera.look_at
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
	ray_screen = np.array([ray_u, ray_v, ray_w]) - camera.look_from
	ray_screen = ray_screen / np.linalg.norm(ray_screen)
	ray_screen = np.append(ray_screen, 1)
	return screen_to_world@translate@ray_screen  # ray in world space


def is_in_shadow(point):
	global epsilon
	shadow_direction = scene.light_direction - point
	shadow_direction = shadow_direction / np.linalg.norm(shadow_direction)
	# ignore shadow_color/obj from this, it doesn't matter
	shadow_color, shadow_intersect = compute_intersections(point + epsilon * shadow_direction,
																	   shadow_direction, 0)
	return True if shadow_intersect is not None else False


# r0 == ray origin, rd == ray direction;
def compute_intersections(r0, rd, spawn_depth):
	global objects, epsilon

	min_dist = float('inf')
	intersect_point = None
	intersect_obj = None
	illumination = np.array([0.0, 0.0, 0.0])
	for obj in objects:
		point = obj.intersect(r0, rd)
		if point is not None:
			distance = cm.distance_3D(r0, point)
			if distance < min_dist:
				min_dist = distance
				intersect_point = point
				intersect_obj = obj
	if intersect_point is None:
		return None, None  # no intersection

	object_norm = intersect_obj.compute_normal(intersect_point)
	reflect_direction = rd - 2 * object_norm * (np.dot(rd, object_norm))
	light_vector = scene.light_direction - 2 * object_norm * (np.dot(scene.light_direction, object_norm))
	light_reflection = light_vector / np.linalg.norm(light_vector)

	obj_luminance = intersect_obj.luminance(scene.ambient_light, scene.light_color, scene.light_direction,
											object_norm, rd, light_reflection, is_in_shadow(intersect_point))
	illumination = np.clip(illumination + obj_luminance, 0.0, 1.0)  # obj_luminance should never be None

	if intersect_obj.ks > 0 and spawn_depth > 0:  # change to use reflectivity/transparency instead of specular
		# calculate and trace reflection/transmission ray (whether reflective or transparent surface)
		reflect_point = intersect_point + epsilon * reflect_direction
		recursive_color, recursive_intersect = compute_intersections(reflect_point, reflect_direction, spawn_depth - 1)
		additive_color = recursive_color if recursive_color is not None else scene.background_color
		illumination = np.clip(illumination + additive_color * intersect_obj.ks, 0.0, 1.0)\

	return illumination, intersect_point


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
		color, intersect_point = compute_intersections(camera.look_from, ray, num_reflections)
		pixel_color = color if color is not None else scene.background_color
		render[i][j] = pixel_color

write_to_ppm()
