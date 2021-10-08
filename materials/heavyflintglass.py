from materials import Material


class HeavyFlintGlass(Material):
	def __init__(self):
		super().__init__(kd, ks, ka, od, os, kgls, 1.89)