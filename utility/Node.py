# Hierarchy Node Class
class Node:
	def __init__(self, subspace, parent):
		self.subspace = subspace
		self.parent = parent
		self.first = None
		self.second = None
		self.children = []  # all objects that belong to the subspace
