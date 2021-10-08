# Hierarchy Node Class
class Node:
	def __init__(self, subspace):
		self.subspace = subspace
		self.first = None
		self.second = None
		self.children = []  # all objects that belong to the subspace
