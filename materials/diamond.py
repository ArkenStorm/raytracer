from materials import Material


class Diamond(Material):
	def __init__(self):
		super().__init__(kd, ks, ka, od, os, kgls, 2.42)