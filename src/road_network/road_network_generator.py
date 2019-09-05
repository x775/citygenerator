# city size: 10.000 m x 10.000 m
# input image size: 1000x1000
# pixel size: 10 m x 10 m

import numpy as np
from enum import Enum
from queue import Queue
from scipy.spatial import cKDTree
from src.road_network.vertex import Vertex
from src.road_network.segment import Segment
from src.road_network.growth_rules.grid import grid
from src.road_network.growth_rules.organic import organic
from src.road_network.helpers import compute_intersection


class Rules(Enum):
    RULE_SEED = 1
    RULE_RADIAL = 2
    RULE_ORGANIC = 3
    RULE_GRID = 4
    RULE_MINOR = 5


def generate_road_network(config):
    segment_added_list = []
    vertex_added_set = set()
    segment_front_queue = Queue(maxsize=0)

    for segment in config.axiom:
        segment_added_list.append(segment)
        segment_front_queue.put(segment)
        vertex_added_set.update([segment.start_vert, segment.end_vert])

    # Iterate through the front queue, incrementally building the road network.
    iteration = 0
    while not segment_front_queue.empty() and iteration < config.max_road_network_iterations:
        current_segment = segment_front_queue.get()

        suggested_segments = generate_suggested_segments(config, current_segment, config.road_rules_array, config.population_density_array)
        verified_segments = verify_segments(config, suggested_segments, segment_added_list, vertex_added_set)
        
        for segment in verified_segments:
            segment_front_queue.put(segment)
            vertex_added_set.update([segment.start_vert, segment.end_vert])
        
        segment_added_list.extend(verified_segments)

        iteration += 1

        # check if segment is seed, if so, readd

    return segment_added_list
        

# INPUT:    ConfigLoader, Segment, numpy.Array, numpy.Array
# OUTPUT:   List
# Generates suggested segments based on the road rule at the end position of the input segment
def generate_suggested_segments(config, segment, rule_image_array, population_image_array):
    roadmap_rule = get_roadmap_rule(segment, rule_image_array)
    population_density = get_population_density_values(segment, normalise_pixel_values(population_image_array))

    if roadmap_rule == Rules.RULE_GRID:
        suggested_segments = grid(config, segment, population_density)
    elif roadmap_rule == Rules.RULE_ORGANIC:
        suggested_segments = organic(config, segment, population_density)
        pass
        # :)
    elif roadmap_rule == Rules.RULE_RADIAL:
        pass
        # :(
    elif roadmap_rule == Rules.RULE_SEED:
        pass
        # hehe
    else: #Rules.RULE_MINOR
        pass

    return suggested_segments
    

#TODO:
# This assumes that the population density image has been converted to 
# black and white, and then all values for whiteness have been computed
# and normalised in the matrix. Thus, we only need to find the matching
# x,y for the vertex we are looking at.
def get_roadmap_rule(segment, image_array):

    return Rules.RULE_ORGANIC

    #if segment.is_seed:
    #    return Rules.RULE_SEED

    #if segment.is_major_road:[0]
        # If we are dealing with a major road, we need to determine whether
        # we need to apply a radial, organic, or grid-based parttern.
        #TODO: Add support for other rules
     #   color = image_array[segment.end.x][segment.end.y]
     #   if color == (r,b,g,a):
     #       return Rules.RULE_GRID
     #   elif color == (r,b,g,a):
     #       return Rules.RULE_ORGANIC
     #   elif color == (r,b,g,a):
     #       return Rules.RULE_RADIAL
    #else:
     #   return Rules.RULE_MINOR
    

# INPUT:    ConfigLoader, Segment, List, Set
# OUTPUT:   List
# Local constraints are used to verify the suggested segments. Segments are
# either ignored if they are out of bounds or altered to fit the existing road network
def verify_segments(config, suggested_segments, segment_added_list, vertex_added_set):
    max_x = config.road_rules_array.shape[1] # maximum x coordinate
    max_y = config.road_rules_array.shape[0] # maximum y coordinate
    max_distance = config.near_vertex_max_distance # maximum allowed distance between road vertices
    vertex_added_list = list(vertex_added_set) # list of unique vertex positions
    # KDTree of unique vertices used to compute nearest neighbours
    vertex_tree = cKDTree([vertex.position for vertex in vertex_added_list])

    verified_segments = []

    # INPUT:    Segment, Segment  
    # OUTPUT:   -
    # Creates a new intersection using the two segments. The existing segment is
    # split into two parts and its reference updated in the segment_added_list.
    def _create_intersection(new_segment, intersecting_segment):
        segment_vector = (segment.end_vert.position - segment.start_vert.position)
        abs_intersection = Vertex(intersection[0] * segment_vector + segment.start_vert.position)
        new_segment = Segment(segment_start=new_segment.start_vert, segment_end=abs_intersection)
        old_segment_split = Segment(segment_start=new_segment.end_vert, segment_end=intersecting_segment.end_vert)
        intersecting_segment.end_vert = new_segment.end_vert

        verified_segments.append(new_segment)
        segment_added_list.append(old_segment_split)
        
        
    for segment in suggested_segments:
        # We do not consider the segment further if it breaks the boundaries.
        if segment.end_vert.position[0] > max_x or segment.end_vert.position[1] > max_y:
            continue 
        
        # We query the KDTree to find the closest vertex to the end position of
        # the new segment. We use k=2 to find the two closest neighbours because
        # the closest vertex will always be the queried vertex itself.
        _, result_indexes = vertex_tree.query(segment.end_vert.position, k=2, distance_upper_bound=max_distance)
        vertex_is_close = False
        closest_value = np.inf
        intersecting_segment = None

        # If the second element of result_indexes is not equal the length
        # of the vertex_added_list, a nearby vertex has been found
        if result_indexes[1] != len(vertex_added_list):
            result_index = result_indexes[1]
            vertex_is_close = True
        
        # TODO: check distance to avoid computing every intersection
        for old_segment in segment_added_list:
            intersection = compute_intersection(segment, old_segment)

            # We check whether the new segment intersects an existing segment.
            # If the relative point of intersection is between 0.00001 and
            # 0.99999, an intersection is detected. If multiple intersections
            # are detected, use the intersection closest to the start position
            # of the new segment.
            if(intersection[0] > 0.00001 and 
               intersection[0] < 0.99999 and 
               intersection[1] > 0.00001 and 
               intersection[1] < 0.99999 and 
               intersection[0] < closest_value):
                intersecting_segment = old_segment 
                closest_value = intersection[0]
        
        # If the segment intersects an existing segment, and an existing vertex
        # is not nearby, we create a new intersection (and thus vertex) and
        # split the existing segment into two parts.
        if intersecting_segment and not vertex_is_close:
            _create_intersection(segment, intersecting_segment)
        
        # If the segment does not intersect an existing segment but is close to
        # an existing vertex, we snap the end position of the segment to the
        # existing vertex.
        elif vertex_is_close and not intersecting_segment:
            close_vertex = vertex_added_list[result_index]
            new_segment = Segment(segment_start=segment.start_vert, segment_end=close_vertex)
            verified_segments.append(new_segment)

        # If the segment intersects an existing segment and is also close to an
        # existing vertex, we consider two different cases: Where the vertex is
        # part of the intersecting segment and not.
        elif vertex_is_close and intersecting_segment:
            close_vertex = vertex_added_list[result_index]
            
            # If the existing vertex is part of the intersecting segment, we
            # snap the end position of the segment to the intersecting segment.
            if (close_vertex is intersecting_segment.start_vert or 
                close_vertex is intersecting_segment.end_vert):
                new_segment = Segment(segment_start=segment.start_vert, segment_end=close_vertex)
                verified_segments.append(new_segment)
            # If the existing vertex is not part of the intersecting segment, we
            # create a new intersection (and thus vertex) and split the existing
            # segment into two parts.
            else:
                _create_intersection(segment, intersecting_segment)
        # If no local constraints apply, and the segment does not break outer
        # bounds, we append it without alterations.
        else:
            verified_segments.append(segment)
    
    return verified_segments


def get_population_density_values(segment, population_image_array):
    return population_image_array[int(segment.end_vert.position[1])][int(segment.end_vert.position[0])]


# normalise pixel values to single value in range [0,1]
def normalise_pixel_values(image_array):
    return image_array[:,:,0] / 255
