# Hierarchy Node Class
class Node:
	def __init__(self, bound_box, parent):
		self.bounding_box = bound_box
		self.parent = parent
		self.first = None
		self.second = None
