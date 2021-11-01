class Material:
	def __init__(self, kd=1.0, ks=0, ka=1.0, od=0, os=0, kgls=0, ri=None):
		self.kd = kd  # diffuse coefficient;
		self.ks = ks  # specular coefficient
		self.ka = ka  # ambient coefficient
		self.od = od  # diffuse reflectance color
		self.os = os  # object specular color
		self.kgls = kgls  # glossy constant
		self.ri = ri  # index of refraction
		# add reflectivity constant/boolean?
		# add transparency constant/boolean?
