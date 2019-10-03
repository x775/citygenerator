import random
import numpy as np
from src.utilities import rotate
from src.road_network.vertex import Vertex
from src.road_network.segment import Segment

# INPUT:    ConfigLoader, Segment, Float
# OUTPUT:   List
def organic(config, segment, population_density):
    road_straight_probability = config.organic_straight_road_probability
    road_turn_probability = config.organic_road_turn_probability
    if segment.is_minor_road:
        road_mininum_length = config.minor_road_min_length
        road_maximum_length = config.minor_road_max_length
    else:
        road_mininum_length = config.organic_road_min_length
        road_maximum_length = config.organic_road_max_length

    suggested_segments = []

    # Compute the unit vector of the given segment to determine direction.
    segment_unit_vector = (segment.end_vert.position - segment.start_vert.position)/segment.segment_norm()

    # Generate a new segment going straight.
    if random.uniform(0, 1) <= road_straight_probability:
        rotated_unit_vector = rotate(segment_unit_vector, random.uniform(-30, 30))
        straight_segment_array = random.uniform(road_mininum_length, road_maximum_length) * rotated_unit_vector
        straight_segment_array += segment.end_vert.position

        new_segment = Segment(segment_start=segment.end_vert, segment_end=Vertex(straight_segment_array))
        suggested_segments.append(new_segment)

    # We multiply the probability with the population density because we want to
    # modestly increase the probability of turning the closer to the density.b
    road_turn_probability = road_turn_probability * (population_density + 1)

    # Generate new segment turning right.
    if random.uniform(0, 1) <= road_turn_probability:
        rotated_unit_vector = rotate(segment_unit_vector, random.uniform(-120, -60))
        turn_road_segment_array = random.uniform(road_mininum_length, road_maximum_length) * rotated_unit_vector
        turn_road_segment_array += segment.end_vert.position

        new_segment = Segment(segment_start=segment.end_vert, segment_end=Vertex(turn_road_segment_array))
        suggested_segments.append(new_segment)
    
    # Generate new segment turning left.
    if random.uniform(0, 1) <= road_turn_probability:
        rotated_unit_vector = rotate(segment_unit_vector, random.uniform(60, 120))
        turn_road_segment_array = random.uniform(road_mininum_length, road_maximum_length) * rotated_unit_vector
        turn_road_segment_array += segment.end_vert.position
        
        new_segment = Segment(segment_start=segment.end_vert, segment_end=Vertex(turn_road_segment_array))
        suggested_segments.append(new_segment)
    
    return suggested_segments