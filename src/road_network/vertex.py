class Vertex:
    def __init__(self, pos):
        self.position = pos # y axis goes from top to bottom of screen
        self.is_intersection = False

    def __hash__(self):
        return hash(tuple(self.position))

    def __eq__(self, other):
        return (self.position == other.position).all()