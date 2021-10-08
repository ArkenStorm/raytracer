from materials import Material


# TODO: Don't worry about this right now, water is wack
class Water(Material):
	def __init__(self):
		super().__init__(0, 0, 0, 0, 0, 0, 1.33)  # TODO: figure out what the heck these constants might be

