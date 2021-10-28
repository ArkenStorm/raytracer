import numpy as np


class Texture:
	def __init__(self, ppm, max_color=255):
		self.ppm = ppm
		self.max_color = max_color

	def get_color(self, u, v):
		u = min(u, 0.999)
		v = min(v, 0.999)
		u = np.fmod(u, 1.0)
		v = np.fmod(v, 1.0)
		if u < 0:
			u = 1 + u
		if v < 0:
			v = 1 + v
		row = int(v * len(self.ppm))
		col = int(u * len(self.ppm[0]))
		return np.array([x / self.max_color for x in self.ppm[row][col]])
