import numpy as np
from src.road_network.vertex import Vertex

class Segment:
    def __init__(self, segment_start=None, segment_end=None, segment_array=None):
        if segment_start and segment_end:
            self.start_vert = segment_start
            self.end_vert = segment_end
        elif segment_array is not None:
            self.start_vert = Vertex(segment_array[0])
            self.end_vert = Vertex(segment_array[1])
        else:
            raise ValueError("segment start and end or segment array must be supplied!")
        self.is_minor_road = False
    
    @classmethod
    def from_verts(cls, start_vert, end_vert):
        return cls(np.array([start_vert.position, end_vert.position]))

    def segment_norm(self):
        return np.linalg.norm(self.end_vert.position - self.start_vert.position)

    def __hash__(self):
        return hash(tuple(self.start_vert.position + self.end_vert.position))

    def __eq__(self, other):
        return ((self.start_vert == other.start_vert and self.end_vert == other.end_vert)
             or (self.start_vert == other.end_vert and self.end_vert == other.start_vert))
