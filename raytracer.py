from object_models import *
from environment import *
import custom_math as cm

image_height = 500
image_width = 500
epsilon = 0.0000001
i_min, j_min = 0, 0
i_max, j_max = image_height - 1, image_width - 1
num_reflections = 1  # max ray tree depth
min_light_val = 0.05  # ????
subdivisions = 1  # number of subdivisions in each dimension

scene_name = "655Lab1.ppm"
render = [[0 for j in range(image_width)] for i in range(image_height)]


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
	return screen_to_world @ translate @ ray_screen  # ray in world space


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

	# reflection ray
	if intersect_obj.material.ks > 0 and spawn_depth > 0:  # calculate and trace reflection ray
		reflect_point = intersect_point + epsilon * reflect_direction
		recursive_color, recursive_intersect = compute_intersections(reflect_point, reflect_direction, spawn_depth - 1)
		additive_color = recursive_color if recursive_color is not None else scene.background_color
		illumination = np.clip(illumination + additive_color * intersect_obj.material.ks, 0.0, 1.0)
	if intersect_obj.material.ri is not None and spawn_depth > 0:  # calculate and trace refraction ray
		pass
	return illumination, intersect_point


def write_to_ppm():
	global image_height, image_width, scene_name, render
	ppm_file = open(scene_name, "w+")

	ppm_file.write(f'P3\n{image_width} {image_height}\n255\n')
	for j in range(image_height - 1, -1, -1):
		write_line = ""
		for i in range(image_width):
			r, g, b = render[i][j]  # RGB tuples stored in the render array
			write_line += f'{r * 255} {g * 255} {b * 255} '
		ppm_file.write(write_line)
	print("All rows written")

	ppm_file.close()


scene, objects, camera = Scene().parse("scenes/655Lab1.rayTracing")
for i in range(image_height):
	for j in range(image_width):
		step = 1 / subdivisions
		subrays = [(i + step * n, j + step * p) for n in range(subdivisions) for p in range(subdivisions)]
		pixel_color = 0
		for x, y in subrays:
			ray = compute_primary_ray(x, y)[:3]
			color, intersection = compute_intersections(camera.look_from, ray, num_reflections)
			pixel_color += color if color is not None else scene.background_color
		render[i][j] = pixel_color / (subdivisions**2)  # average pixel color by number of subrays

write_to_ppm()
