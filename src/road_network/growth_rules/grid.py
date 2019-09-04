import random
import numpy as np
from src.road_network.helpers import rotate
from src.road_network.segment import Segment

def grid(segment, population_density):
    road_straight_probability = 1  # [0,1]
    road_turn_probability = 0.1  # [0,1]
    road_mininum_length = 5
    road_maximum_length = 5

    suggested_segments = []

    # Compute the unit vector of the given segment to determine direction.
    segment_unit_vector = (segment.end_vert.position - segment.start_vert.position)/segment.segment_norm()

    # Generate new segment going straight
    if random.uniform(0, 1) <= road_straight_probability:
        straight_segment_array = random.uniform(road_mininum_length, road_maximum_length) * segment_unit_vector
        straight_segment_array += segment.end_vert.position
        new_segment_array = np.array([segment.end_vert.position, straight_segment_array])
        new_segment = Segment(segment_array=new_segment_array)
        new_segment.is_seed = True
        suggested_segments.append(new_segment)

    # We multiply the probability with the population density twice because
    # we want to increase the probability of turning the closer to the density.  
    road_turn_probability = road_turn_probability * population_density ** 2
    
    # Rotate unit vector 90 degrees.
    rotated_unit_vector = rotate(segment_unit_vector, 90)

    turn_road_segment_array = random.uniform(road_mininum_length, road_maximum_length) * rotated_unit_vector
    turn_road_segment_array_left = random.uniform(road_mininum_length, road_maximum_length) * -rotated_unit_vector
    turn_road_segment_array += segment.end_vert.position
    turn_road_segment_array_left += segment.end_vert.position
    
    # Generate new segment turning right
    if random.uniform(0, 1) <= road_turn_probability:
        new_segment_array = np.array([segment.end_vert.position, turn_road_segment_array])
        new_segment = Segment(segment_array=new_segment_array)
        new_segment.is_seed = False
        suggested_segments.append(new_segment)

    # Generate new segment turning left
    if random.uniform(0, 1) <= road_turn_probability:
        new_segment_array = np.array([segment.end_vert.position, turn_road_segment_array_left])
        new_segment = Segment(segment_array=new_segment_array)
        new_segment.is_seed = False
        suggested_segments.append(new_segment)

    return suggested_segments