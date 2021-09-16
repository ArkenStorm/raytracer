import numpy as np
from environment import Camera
from object_models import *
from materials import *
import materials


class Scene:
	def __init__(self):  # TODO: account for multiple directional light sources?
		self.light_direction = None
		self.light_color = None
		self.ambient_light = None
		self.background_color = None
		self.light_sources = []  # TODO: make a list of all lights

	def parse(self, filepath):  # TODO: bounding volumes for objects
		scene_info = open(filepath)
		objects = []
		custom_materials = []

		camera_vals = scene_info.readline().split()
		look_at, look_from, look_up, fov = np.array(list(map(float, camera_vals[1:4]))),\
										   np.array(list(map(float, camera_vals[4:7]))),\
										   np.array(list(map(float, camera_vals[7:10]))), float(camera_vals[10])

		camera = Camera(look_at, look_from, look_up, fov)

		self.background_color = np.array(list(map(float, scene_info.readline().split()[1:])))
		self.ambient_light = np.array(list(map(float, scene_info.readline().split()[1:])))

		while line := scene_info.readline().split():
			if line[0].lower() == "directional_light":
				self.light_direction, self.light_color = np.array(list(map(float, line[1:4]))), \
														 np.array(list(map(float, line[4:])))
				# TODO: edit to not have the self variables
				self.light_sources.append({"direction": self.light_direction, "color": self.light_color})
			elif line[0].lower() == "point_light":
				point_light_pos, point_light_color = np.array(list(map(float, line[1:4]))), \
													 np.array(list(map(float, line[4:])))
				self.light_sources.append({"pos": point_light_pos, "color": point_light_color})
			# TODO: Area lights, sphere lights
			if line[0].lower() == "material":
				kd = float(line[2])
				ks = float(line[4])
				ka = float(line[6])
				od = np.array(list(map(float, line[8:11])))
				os = np.array(list(map(float, line[12:15])))
				kgls = int(line[16])
				ri = None if line[18] == "None" else float(line[18])
				custom_materials.append(Material(kd, ks, ka, od, os, kgls, ri))
			elif line[0].lower() == "sphere":  # TODO: indices are wrong when not using custom materials
				if line[1].lower() == "custom":
					mat = custom_materials[int(line[2])]
				else:
					mat = getattr(materials, line[1])
					# TODO: error check
				center = list(map(float, line[2:5]))
				radius = float(line[6])

				objects.append(Sphere(center, radius, mat))
			elif line[0].lower() == "triangle":
				if line[1].lower() == "custom":
					mat = custom_materials[int(line[2])]
				else:
					mat = getattr(materials, line[1])
				vertices = [np.array(list(map(float, line[3:6]))), np.array(list(map(float, line[6:9]))),
							np.array(list(map(float, line[9:])))]

				objects.append(Triangle(vertices, mat))
			else:
				pass  # render other polygons eventually
		return self, objects, camera
