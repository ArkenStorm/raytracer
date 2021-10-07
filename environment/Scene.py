from utility import Node
from object_models import Box


class Scene:
	def __init__(self, ambient, background, lights, objects, camera, custom_materials):
		self.ambient_light = ambient
		self.background_color = background
		self.light_sources = lights
		self.objects = objects
		self.camera = camera
		self.custom_materials = custom_materials
		self.hierarchy = None  # set to tree root
		self.max_subspaces = 20  # set as constant for simplicity
		self.max_objects = 3
		# TODO: set default scene material

	def generate_hierarchy(self):
		# Find x, y, z min/max of all objects
		scene_x_min, scene_x_max = -float('inf'), float('inf')
		scene_y_min, scene_y_max = -float('inf'), float('inf')
		scene_z_min, scene_z_max = -float('inf'), float('inf')
		for o in self.objects:
			o_min_vals, o_max_vals = o.get_bounding_box()
			scene_x_min, scene_x_max = min(o_min_vals[0], scene_x_min), max(o_max_vals[0], scene_x_max)
			scene_y_min, scene_y_max = min(o_min_vals[1], scene_y_min), max(o_max_vals[1], scene_y_max)
			scene_z_min, scene_z_max = min(o_min_vals[2], scene_z_min), max(o_max_vals[2], scene_z_max)
		# Bounding box of the whole scene
		omnibox = Box([scene_x_min, scene_y_min, scene_z_min], [scene_x_max, scene_y_max, scene_z_max], None)
		root = Node(omnibox, None)
		subspaces = 0

		pass

