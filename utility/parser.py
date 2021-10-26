from utility import TextureMapper
from environment import *
from object_models import *
from materials import *
import materials


class Parser:
	def __init__(self):
		self.custom_materials = []
		return

	@staticmethod
	def get_material(name):
		try:
			mat = getattr(materials, name)
			return mat
		except AttributeError:
			print("Invalid material provided.\nValid Materials:")
			print("\n\t".join([c for c in valid_materials.values()]))

	def determine_material(self, line):
		mat, tex = Material(), None
		if line[1].lower() == "custom":
			start_index = 3
			mat = self.custom_materials[int(line[2])]
		elif line[1].lower() == "texture":
			if line[2].lower() == "custom":
				start_index = 4
				tex = TextureMapper.create_texture(line[3])
			else:
				start_index = 3
				tex = None  # TODO: create some prebuilt textures?

		elif line[1].lower() == "area_light":
			start_index = 5  # start after the light color
			area_light_color = np.array(list(map(float, line[2:5])))
			mat = Parser.get_material("AreaLight")(area_light_color)
		else:
			start_index = 2
			mat = Parser.get_material(valid_materials[line[1].lower()])()
		return mat, tex, start_index

	@staticmethod
	def parse_material(line):
		kd = float(line[2])
		ks = float(line[4])
		ka = float(line[6])
		od = np.array(list(map(float, line[8:11])))
		os = np.array(list(map(float, line[12:15])))
		kgls = float(line[16])
		ri = None if line[18] == "None" else float(line[18])
		return Material(kd, ks, ka, od, os, kgls, ri)

	def parse_sphere(self, line):
		mat, tex, coord_start = self.determine_material(line)
		center = list(map(float, line[coord_start:coord_start + 3]))
		radius = float(line[coord_start + 3])
		return Sphere(center, radius, mat, tex)

	def parse_triangle(self, line):
		mat, tex, coord_start = self.determine_material(line)
		vertices = [np.array(list(map(float, line[coord_start:coord_start + 3]))),
					np.array(list(map(float, line[coord_start + 3:coord_start + 6]))),
					np.array(list(map(float, line[coord_start + 6:])))]
		return Triangle(vertices, mat, tex)

	def parse_plane(self, line):
		pass

	def parse_box(self, line):
		mat, tex, coord_start = self.determine_material(line)
		max_vals = list(map(float, line[coord_start: coord_start + 3]))
		min_vals = list(map(float, line[coord_start + 3: coord_start + 6]))
		# Bounds checking
		if max_vals[0] < min_vals[0]:
			max_vals[0], min_vals[0] = min_vals[0], max_vals[0]
		if max_vals[1] < min_vals[1]:
			max_vals[1], min_vals[1] = min_vals[1], max_vals[1]
		if max_vals[2] < min_vals[2]:
			max_vals[2], min_vals[2] = min_vals[2], max_vals[2]
		return Box(min_vals, max_vals, mat, tex)  # Do the min/max vals need to be np arrays?

	def parse_scene(self, filepath):
		lights, objs, custom_mats = [], [], []

		scene_info = open(filepath)

		camera_vals = scene_info.readline().split()
		look_at, look_from, look_up, fov = np.array(list(map(float, camera_vals[1:4]))), \
										   np.array(list(map(float, camera_vals[4:7]))), \
										   np.array(list(map(float, camera_vals[7:10]))), float(camera_vals[10])

		camera = Camera(look_at, look_from, look_up, fov)

		bg_color = np.array(list(map(float, scene_info.readline().split()[1:])))
		ambience = np.array(list(map(float, scene_info.readline().split()[1:])))

		while line := scene_info.readline().split():
			if line[0].lower() == "directional_light":
				light_direction, light_color = np.array(list(map(float, line[1:4]))), \
											   np.array(list(map(float, line[4:])))
				lights.append({"direction": light_direction, "color": light_color})
			elif line[0].lower() == "point_light":
				point_light_pos, point_light_color = np.array(list(map(float, line[1:4]))), \
													 np.array(list(map(float, line[4:])))
				lights.append({"pos": point_light_pos, "color": point_light_color})
			# Area Lights handled as a material
			elif line[0].lower() == "material":
				self.custom_materials.append(Parser.parse_material(line))
			elif line[0].lower() == "sphere":
				new_sphere = self.parse_sphere(line)
				if isinstance(new_sphere.material, AreaLight):
					lights.append({"object": new_sphere})
				objs.append(new_sphere)
			elif line[0].lower() == "triangle":
				new_triangle = self.parse_triangle(line)
				if isinstance(new_triangle.material, AreaLight):
					lights.append({"object": new_triangle})
				objs.append(new_triangle)
			elif line[0].lower() == "plane":
				pass
			elif line[0].lower() == "box":
				new_box = self.parse_box(line)
				if isinstance(new_box.material, AreaLight):
					lights.append({"object": new_box})
				objs.append(new_box)
			else:
				pass  # render other polygons eventually
		return Scene(ambience, bg_color, lights, objs, camera, self.custom_materials)
