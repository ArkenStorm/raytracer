from materials import Material


class FusedQuartz(Material):
	def __init__(self):
		super().__init__(kd, ks, ka, od, os, kgls, 1.46)