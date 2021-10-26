from textures import Texture
import re


class TextureMapper:
	def __init__(self):
		pass

	@staticmethod
	# create an instance of the texture class and return it.
	def create_texture(path):
		# needs to be a ppm file
		image = open(path)
		image.readline()  # skip the P3/P6
		width, height = map(int, image.readline().split(" "))
		max_color = int(image.readline())
		tex = []
		# stupid gimp not exporting things according to ppm standard
		# while row := image.readline().split(' '):
		# 	if row[0] == "":
		# 		break
		# 	row_pixels = [(float(row[j]), float(row[j+1]), float(row[j+2])) for j in range(0, width * 3, 3)]
		# 	tex.append(row_pixels)
		rgb_vals = image.read()
		rgb_vals = list(map(float, filter(lambda x: x != '', re.split(r'\s', rgb_vals))))
		for i in range(0, len(rgb_vals), width * 3):
			row_pixels = [(rgb_vals[j], rgb_vals[j+1], rgb_vals[j+2]) for j in range(i, i + width * 3, 3)]
			tex.append(row_pixels)

		return Texture(tex, max_color)
