from materials import Material


class CrownGlass(Material):
	def __init__(self):
		super().__init__(kd, ks, ka, od, os, kgls, 1.52)