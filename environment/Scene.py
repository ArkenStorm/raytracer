class Scene:
	def __init__(self, ambient, background, lights, objects, camera, custom_materials):
		self.ambient_light = ambient
		self.background_color = background
		self.light_sources = lights
		self.objects = objects
		self.camera = camera
		self.custom_materials = custom_materials
		# TODO: set default scene material

	# TODO: bounding volume hierarchy; set up BVH tree
