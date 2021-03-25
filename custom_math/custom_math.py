import numpy as np


def cross_norm(a, b, normalize=True):
	ax, ay, az = a
	bx, by, bz = b

	cx = ay * bz - az * by
	cy = az * bx - ax * bz
	cz = ax * by - ay * bx

	norm = (cx * cx + cy * cy + cz * cz)**0.5
	return np.array([cx / norm, cy / norm, cz / norm]) if normalize else np.array([cx, cy, cz])


def distance_2D(a, b):
	x1, y1 = a
	x2, y2 = b
	return ((x2-x1)**2)+((y2-y1)**2)**0.5


# find the distance between two 3D points
def distance_3D(a, b):
	x1, y1, z1 = a
	x2, y2, z2 = b
	return (((x2-x1)**2)+((y2-y1)**2)+((z2-z1)**2))**(1/2)