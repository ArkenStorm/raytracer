class Material:
	def __init__(self, kd, ks, ka, od, os, kgls, ri):
		self.kd = kd  # diffuse coefficient;
		self.ks = ks  # specular coefficient
		self.ka = ka  # ambient coefficient
		self.od = od  # diffuse reflectance color
		self.os = os  # object specular color
		self.kgls = kgls  # glossy constant
		self.ri = ri  # index of refraction
		# add reflectivity constant/boolean?
		# add transparency constant/boolean?
