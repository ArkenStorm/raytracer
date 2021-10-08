from object_models import Object


# General Polygon intersection class TODO: FIX THIS CLASS
class Polygon(Object):
	def __init__(self, kd, ks, ka, od, os, kgls):
		super().__init__(kd, ks, ka, od, os, kgls)
		return


# num_crossings logic; debug eventually; general polygonal intersection
# dominant_index = np.argmax(normal)
# proj_vertices = []
# proj_point = np.delete(r0, dominant_index)
# for vertex in self.vertices:
# 	proj_vertices.append(np.delete(vertex, dominant_index) - proj_point)
# num_crossings = 0
# sign_holder = -1 if proj_vertices[0][1] < 0 else 1
# for i, vertex in enumerate(proj_vertices):
# 	next_i = (i + 1) % len(proj_vertices)
# 	next_sign_holder = -1 if proj_vertices[next_i][1] < 0 else 1
# 	if sign_holder != next_sign_holder:
# 		if proj_vertices[i][0] > 0 and proj_vertices[next_i][0]:
# 			num_crossings += 1
# 		elif proj_vertices[i][0] > 0 or proj_vertices[next_i][0]:
# 			u_cross = proj_vertices[i][0] - proj_vertices[i][1] * (proj_vertices[next_i][0] - proj_vertices[i][0]) / (proj_vertices[next_i][1] - proj_vertices[i][1])
# 			if u_cross > 0:
# 				num_crossings += 1
# 	sign_holder = next_sign_holder
# return intersect_point if num_crossings % 2 == 1 else None
