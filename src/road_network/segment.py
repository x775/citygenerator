import numpy as np
from vertex import Vertex

class Segment:
    def __init__(self, segment_array):
        self.start_vert = Vertex(segment_array[0])
        self.end_vert = Vertex(segment_array[1])
        self.is_seed = False
        self.is_major_road = False
    
    @classmethod
    def from_verts(cls, start_vert, end_vert):
        return cls(np.array([start_vert.position, end_vert.position]))

    def segment_norm(self):
        return np.linalg.norm(self.end_vert.position - self.start_vert.position)
