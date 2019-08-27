import numpy as np

def grid(vertex, population_density):
    road_forward_probability = 1  # [0,1]
    road_turn_probability = 0.1  # [0,1]
    road_mininum_length = 1
    road_maximum_length = 20

    suggested_vertices = []

    previous_vector = 