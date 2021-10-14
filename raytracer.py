import numpy as np
from ray import Ray
from utility import Parser
from utility import custom_math as cm
from materials import AreaLight
from multiprocessing import Pool
import time

image_height = 300
image_width = 300
epsilon = 0.000001
i_min, j_min = 0, 0
i_max, j_max = image_height - 1, image_width - 1
num_reflections = 1  # max ray tree depth
min_light_val = 0.05  # ????
pixel_subdivisions = 3  # number of pixel subdivisions in each dimension
num_processes = 6
scene, objects, camera = None, None, None
render = None

scene_name = "testing.ppm"


def compute_primary_ray(i, j):  # i, j are viewport points
	global camera

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


def is_in_shadow(point, norm, light):
	if "object" in light:
		light_normal = point - light["object"].get_position()
		shadow_direction = light["object"].sample_surface(light["object"].get_position() - point, point, norm, light_normal)
	else:
		shadow_direction = light["direction"] - point if "direction" in light else light["pos"] - point
		shadow_direction /= np.linalg.norm(shadow_direction)
	shadow_ray = Ray(point + epsilon * shadow_direction, shadow_direction, None)
	shadow_obj, shadow_intersect, shadow_dist = compute_intersections(shadow_ray, scene.root)
	if shadow_intersect is None:
		return False
	return False if isinstance(shadow_obj.material, AreaLight) else True


def compute_intersections(r, node):
	# TODO: add parent to node, try and be smart about traversal? Keep track of current node/space ray is in?

	if node.first is None:  # both first and second will be None in this case
		min_dist = float('inf')
		final_point = None
		final_obj = None

		for obj in node.children:
			point = obj.intersect(r)
			if point is not None:
				distance = cm.distance_3D(r.origin, point)
				if distance < min_dist:
					min_dist = distance
					final_point = point
					final_obj = obj
		if final_point is None:
			return None, None, None  # no intersection
		return final_obj, final_point, min_dist
	else:
		o1, p1, d1 = None, None, None
		o2, p2, d2 = None, None, None
		if node.first.subspace.intersect(r) is not None:
			o1, p1, d1 = compute_intersections(r, node.first)
		if node.second.subspace.intersect(r) is not None:
			o2, p2, d2 = compute_intersections(r, node.second)

		# the ray intersects no objects in this subspace
		if d1 is None and d2 is None:
			return None, None, None

		if d1 is not None:
			if d2 is None:
				return o1, p1, d1
			return (o1, p1, d1) if d1 < d2 else (o2, p2, d2)

		if d2 is not None:
			if d1 is None:
				return o2, p2, d2
			return (o2, p2, d2) if d2 < d1 else (o1, p1, d1)


def compute_lighting(r, obj, point, norm):
	global scene
	if obj in scene.light_sources:  # The obj is an area light
		return obj.material.color

	illumination = np.array([0.0, 0.0, 0.0])
	# TODO: Add intensity on lighting
	for light_source in scene.light_sources:
		if "object" in light_source:
			area_light = light_source["object"]
			light_direction = area_light.sample_surface(area_light.get_position() - point, point, norm,
														point - area_light.get_position())
			light_color = light_source["object"].material.color
		else:
			light_direction = light_source["direction"] if "direction" in light_source else light_source["pos"]
			light_color = light_source["color"]
		light_vector = light_direction - 2 * norm * (np.dot(light_direction, norm))
		light_reflection = light_vector / np.linalg.norm(light_vector)
		# what should jitter factor be?
		obj_luminance = obj.luminance(scene.ambient_light, light_color, light_direction, norm,
												r.dir, light_reflection, is_in_shadow(point, norm, light_source))
		illumination += illumination + obj_luminance  # obj_luminance should never be None
	# average the illumination of all the lights shining on the object
	illumination = np.clip(illumination / len(scene.light_sources), 0.0, 1.0)
	return illumination


def trace_reflections(illumination, r, obj, point, norm, spawn_depth):
	reflect_direction = r.dir - 2 * norm * (np.dot(r.dir, norm))
	reflect_point = point + epsilon * reflect_direction
	reflection_ray = Ray(reflect_point, reflect_direction, None)
	recursive_color, recursive_intersect = trace_ray(reflection_ray.jitter(obj.material.kgls), spawn_depth - 1)
	additive_color = recursive_color if recursive_color is not None else scene.background_color
	illumination = np.clip(illumination + additive_color * obj.material.ks, 0.0, 1.0)
	return illumination


def trace_refractions(illumination, r, obj, point, norm, spawn_depth):
	# TODO: keep track of what material the ray is currently in for internal refraction
	index_refraction = 1.003 / obj.material.ri
	cos_theta = np.dot(norm, -r.dir) / (np.linalg.norm(norm) * np.linalg.norm(r.dir))
	refract_direction = index_refraction * r.dir + \
						(index_refraction * cos_theta -
						 (1 + (index_refraction ** 2) * ((cos_theta ** 2) - 1)) ** 0.5) * norm
	start_refract_point = point + epsilon * refract_direction
	# this doesn't work for non-3D objects
	internal_ray = Ray(start_refract_point, refract_direction, None)
	end_refract_point = obj.intersect(internal_ray.jitter(obj.material.kgls)) + epsilon * refract_direction

	# the ray goes back to the original direction <-- is this true?
	# TODO: Handle internal refraction
	refraction_ray = Ray(end_refract_point, r.dir, None)
	recursive_color, recursive_intersect = trace_ray(refraction_ray.jitter(obj.material.kgls), spawn_depth)
	additive_color = recursive_color if recursive_color is not None else scene.background_color
	illumination = np.clip(illumination + additive_color + (obj.material.od * obj.material.kd), 0.0, 1.0)
	return illumination


# r0 == ray origin, rd == ray direction;
def trace_ray(r, spawn_depth):
	global scene

	intersect_obj, intersect_point, intersect_dist = compute_intersections(r, scene.root)
	if intersect_obj is None:
		return None, None
	if isinstance(intersect_obj.material, AreaLight):
		return intersect_obj.material.color, intersect_point

	object_norm = intersect_obj.compute_normal(intersect_point)
	illumination = compute_lighting(r, intersect_obj, intersect_point, object_norm)

	# calculate and trace reflection ray
	if intersect_obj.material.ks > 0 and spawn_depth > 0:
		illumination = trace_reflections(illumination, r, intersect_obj, intersect_point, object_norm, spawn_depth)

	# calculate and trace refraction ray; spawn depth checked because of internal refraction
	if intersect_obj.material.ri is not None and spawn_depth > 0:
		illumination = trace_refractions(illumination, r, intersect_obj, intersect_point, object_norm, spawn_depth)

	return illumination, intersect_point


def write_to_ppm():
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


def compute_pixel(pixel):
	i, j = pixel
	step = 1 / pixel_subdivisions
	subrays = [(i + step * n, j + step * p) for n in range(pixel_subdivisions) for p in range(pixel_subdivisions)]
	p_color = 0  # pixel_color
	for x, y in subrays:
		ray_direction = compute_primary_ray(x, y)[:3]
		primary_ray = Ray(camera.look_from, ray_direction, None)  # TODO: starting ray material
		color, intersection = trace_ray(primary_ray, num_reflections)
		p_color += color if color is not None else scene.background_color
	p_color /= (pixel_subdivisions ** 2)  # average pixel color by number of subrays
	return p_color, i, j


def setup(global_vars, pixel):
	global scene, objects, camera
	scene = global_vars['scene']
	objects = global_vars['objects']
	camera = global_vars['camera']
	return compute_pixel(pixel)


if __name__ == '__main__':
	start_time = time.time()
	render = [[0 for j in range(image_width)] for i in range(image_height)]
	# TODO: programmatic scene generation
	scene = Parser().parse_scene("scenes/testing.rayTracing")

	hierarchy_time = time.time()
	scene.generate_hierarchy()
	print("Time to generate BVH: " + str(time.time() - hierarchy_time) + " seconds.")

	total_pixels = image_height * image_width
	pixel_chunk_size = (total_pixels - (total_pixels % num_processes)) // num_processes
	shared_vars = {'scene': scene, 'objects': scene.objects, 'camera': scene.camera}

	all_pixels = [(shared_vars, (h, w)) for h in range(image_height) for w in range(image_width)]
	with Pool(num_processes) as pool:
		res = pool.starmap(setup, all_pixels, pixel_chunk_size)
		for pixel_color, i, j in res:
			render[i][j] = pixel_color

	write_to_ppm()
	seconds_elapsed = int(time.time() - start_time)
	m, s = divmod(seconds_elapsed, 60)
	h, m = divmod(m, 60)
	print(f"Total time elapsed: {h:d}:{m:02d}:{s:02d}")
