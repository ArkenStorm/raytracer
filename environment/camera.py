from utility import custom_math as cm
import numpy as np
from math import radians as rad


class Camera:
	def __init__(self, la, lf, lu, fov):
		self.look_at = la
		self.look_from = lf
		self.look_up = lu
		self.fov = fov  # field of view
		self.w = (self.look_from - self.look_at) / np.linalg.norm(self.look_from - self.look_at)
		self.u = cm.cross_norm(self.look_up, self.w)
		self.v = cm.cross_norm(self.w, self.u)
		self.u_max = np.tan(rad(self.fov / 2)) * np.linalg.norm(self.look_at - self.look_from)
		self.u_min = -self.u_max
		self.v_max = np.tan(rad(self.fov / 2)) * np.linalg.norm(self.look_at - self.look_from)
		self.v_min = -self.v_max
