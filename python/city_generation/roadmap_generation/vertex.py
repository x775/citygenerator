class Vertex:
    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.neighbours = []
        self.is_main_road = False
        self.is_seed = False