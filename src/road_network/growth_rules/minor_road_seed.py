import random
import numpy as np
from src.utilities import rotate
from src.road_network.vertex import Vertex
from src.road_network.segment import Segment

# INPUT:    ConfigLoader, Segment, Float
# OUTPUT:   List
def minor_road_seed(config, segment, population_density):
    probability_seed = config.minor_road_seed_probability
    road_mininum_length = config.minor_road_min_length
    road_maximum_length = config.minor_road_max_length
    
    suggested_segments = []

    # Compute the unit vector of the given segment to determine direction.
    segment_unit_vector = (segment.end_vert.position - segment.start_vert.position)/segment.segment_norm()

    # We multiply the probability with the population density because we want to
    # modestly increase the probability of turning the closer to the density.
    road_turn_probability = probability_seed * (population_density + 1)

    # Rotate unit vector 90 degrees.
    rotated_unit_vector = rotate(segment_unit_vector, 90)

    # Generate segment turning right.
    if random.uniform(0, 1) <= road_turn_probability:
        turn_road_segment_array = random.uniform(road_mininum_length, road_maximum_length) * rotated_unit_vector
        turn_road_segment_array += segment.end_vert.position

        new_segment = Segment(segment_start=segment.end_vert, segment_end=Vertex(turn_road_segment_array))
        new_segment.is_minor_road = True
        suggested_segments.append(new_segment)
        

    # Generate segment turning left.
    if random.uniform(0, 1) <= road_turn_probability:
        turn_road_segment_array_left = random.uniform(road_mininum_length, road_maximum_length) * -rotated_unit_vector
        turn_road_segment_array_left += segment.end_vert.position

        new_segment = Segment(segment_start=segment.end_vert, segment_end=Vertex(turn_road_segment_array_left))
        new_segment.is_minor_road = True
        suggested_segments.append(new_segment)

    return suggested_segments
