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
from src.road_network.growth_rules.radial import radial
from src.road_network.growth_rules.organic import organic
from src.utilities import compute_intersection
import math


class Rules(Enum):
    RULE_SEED = 1
    RULE_RADIAL = 2
    RULE_ORGANIC = 3
    RULE_GRID = 4
    RULE_MINOR = 5


def generate_road_network(config):
    segment_added_list = []
    vertex_added_dict = {}
    segment_front_queue = Queue(maxsize=0)

    for segment in config.axiom:
        segment_added_list.append(segment)
        segment_front_queue.put(segment)
        vertex_added_dict[segment.start_vert] = [segment]
        vertex_added_dict[segment.end_vert] = [segment]
        # vertex_added_set.update([segment.start_vert, segment.end_vert])

    # Iterate through the front queue, incrementally building the road network.
    iteration = 0
    while not segment_front_queue.empty() and iteration < config.max_road_network_iterations:
        current_segment = segment_front_queue.get()

        suggested_segments = generate_suggested_segments(config, current_segment, config.road_rules_array, config.population_density_array)
        
        for segment in suggested_segments:
            verified_segment = verify_segment(config, segment, segment_added_list, vertex_added_dict)
            if verified_segment:
                segment_front_queue.put(verified_segment)
                segment_added_list.append(verified_segment)
                for vert in [verified_segment.start_vert, verified_segment.end_vert]:
                    if vert in vertex_added_dict:
                        vertex_added_dict[vert].append(verified_segment)
                    else:
                        vertex_added_dict[vert] = [verified_segment]

            # vertex_added_set.update([segment.start_vert, segment.end_vert])

        iteration += 1

        # check if segment is seed, if so, readd

    return segment_added_list
        

# INPUT:    ConfigLoader, Segment, numpy.Array, numpy.Array
# OUTPUT:   List
# Generates suggested segments based on the road rule at the end position of the input segment
def generate_suggested_segments(config, segment, rule_image_array, population_image_array):
    roadmap_rule = get_roadmap_rule(config, segment, rule_image_array)
    population_density = get_population_density_values(segment, normalise_pixel_values(population_image_array))

    if roadmap_rule == Rules.RULE_GRID:
        suggested_segments = grid(config, segment, population_density)
    elif roadmap_rule == Rules.RULE_ORGANIC:
        suggested_segments = organic(config, segment, population_density)
    elif roadmap_rule == Rules.RULE_RADIAL:
        suggested_segments = radial(config, segment, population_density)
    elif roadmap_rule == Rules.RULE_SEED:
        pass
        # hehe
    else: #Rules.RULE_MINOR
        pass

    return suggested_segments
    

def get_roadmap_rule(config, segment, image_array):

    if segment.is_seed:
        return Rules.RULE_SEED
    elif segment.is_minor_road:
        return Rules.RULE_MINOR
    else:
        # If we are dealing with a major road, we need to determine whether we
        # need to apply a radial, organic, or grid-based parttern.
        y = int(round(segment.end_vert.position[1]))
        x = int(round(segment.end_vert.position[0]))
        color = image_array[y,x]
        if np.array_equal(color, config.grid_legend):
            return Rules.RULE_GRID
        elif np.array_equal(color, config.organic_legend):
            return Rules.RULE_ORGANIC
        elif np.array_equal(color, config.radial_legend):
            return Rules.RULE_RADIAL
    

# INPUT:    ConfigLoader, Segment, List, Set
# OUTPUT:   Segment
# Local constraints are used to verify a suggested segment. Segments are
# either ignored if they are out of bounds or altered to fit the existing road network
def verify_segment(config, segment, segment_added_list, vertex_added_dict):
    max_x = config.road_rules_array.shape[1] # maximum x coordinate
    max_y = config.road_rules_array.shape[0] # maximum y coordinate
    max_distance = config.near_vertex_max_distance # maximum allowed distance between road vertices
    vertex_added_list = list(vertex_added_dict.keys()) # list of unique vertex positions
    # KDTree of unique vertices used to compute nearest neighbours
    vertex_tree = cKDTree([vertex.position for vertex in vertex_added_list])

    # INPUT:    Segment, Segment  
    # OUTPUT:   Segment
    # Creates a new intersection using the two segments. The existing segment is
    # split into two parts and its reference updated in the segment_added_list.
    def _create_intersection(new_segment, intersecting_segment, intersection_value):
        segment_vector = (segment.end_vert.position - segment.start_vert.position)
        abs_intersection = Vertex(intersection_value * segment_vector + segment.start_vert.position)
        new_segment = Segment(segment_start=new_segment.start_vert, segment_end=abs_intersection)
        old_segment_split = Segment(segment_start=new_segment.end_vert, segment_end=intersecting_segment.end_vert)
        intersecting_segment.end_vert = new_segment.end_vert

        # We update the dictionary with vertices and their segments to match the new intersection
        vertex_added_dict[abs_intersection] = [intersecting_segment, old_segment_split]
        vertex_added_dict[old_segment_split.end_vert].remove(intersecting_segment)
        vertex_added_dict[old_segment_split.end_vert].append(old_segment_split)

        segment_added_list.append(old_segment_split)
        return new_segment
        
    # We do not consider the segment further if it breaks the boundaries.
    if segment.end_vert.position[0] > max_x or segment.end_vert.position[1] > max_y:
        return None 
        
    # We query the KDTree to find the closest vertex to the end position of
    # the new segment. We use k=2 to find the two closest neighbours because
    # the closest vertex will always be the queried vertex itself.
    _, result_index = vertex_tree.query(segment.end_vert.position, k=1, distance_upper_bound=max_distance)
    vertex_is_close = False
    avoid_duplicate = False
    closest_value = np.inf
    intersecting_segment = None

    # If the second element of result_index is not equal the length
    # of the vertex_added_list, a nearby vertex has been found
    if result_index != len(vertex_added_list):
        close_vertex = vertex_added_list[result_index]

        if close_vertex is not segment.start_vert:
            # if the close vertex belongs to a segment which shares
            # a vertex with the current segment, the current segment
            # should not snap to the vertex
            close_vertex_segments = vertex_added_dict.get(close_vertex)
            segments_same_start = [seg for seg in close_vertex_segments
                                if segment.start_vert is seg.start_vert or segment.start_vert is seg.end_vert]
            if segments_same_start:
                avoid_duplicate = True

            vertex_is_close = True
    
    # We find the maximum allowed segment length and query our tree to find any
    # vertices within this distance. This way, we reduce the number of segments
    # to check in the subsequent steps; assuming the query returns more than one
    # result. If only one result is returned, it is the segment.end_vert.
    max_segment_length = max(config.grid_road_max_length, config.organic_road_max_length, config.radial_road_max_length)
    _, vertices_indexes = vertex_tree.query(segment.end_vert.position, k=100, distance_upper_bound=max_segment_length+1)
    vertices_indexes = [index for index in vertices_indexes if index != len(vertex_added_list)]
    if vertices_indexes:
        matched_vertices = [vertex_added_list[index] for index in vertices_indexes
                            if vertex_added_list[index] is not segment.end_vert and vertex_added_list[index] is not segment.start_vert]
                                    
        # We find all segments which the matched vertices are part of.
        matched_segments = set()
        for vertex in matched_vertices:
            matched_segments.update(vertex_added_dict[vertex])

        # We compute intersections for all matched segments.
        for old_segment in matched_segments:
            intersection = compute_intersection(segment, old_segment)

            # We check whether the new segment intersects an existing segment.
            # If the relative point of intersection is between 0.00001 and
            # 0.99999 for the existing segment, an intersection is detected. We
            # check whether the relative point of intersection is a bit further
            # beyond the intersection for the new segment in order to extend it
            # if is close to an existing segment. If multiple intersections are
            # detected, use the intersection closest to the start position of
            # the new segment.
            if(intersection[0] > 0.00001 and 
                intersection[0] < 1.49999 and 
                intersection[1] > 0.00001 and 
                intersection[1] < 0.99999 and 
                intersection[0] < closest_value):
                intersecting_segment = old_segment 
                closest_value = intersection[0]
    

    # If the segment intersects an existing segment, and an existing vertex
    # is not nearby, we create a new intersection (and thus vertex) and
    # split the existing segment into two parts.
    if intersecting_segment and not vertex_is_close:
        return _create_intersection(segment, intersecting_segment, closest_value)
        
    # If the segment does not intersect an existing segment but is close to
    # an existing vertex, we snap the end position of the segment to the
    # existing vertex.
    elif vertex_is_close and not intersecting_segment:
        if not avoid_duplicate:
            new_segment = Segment(segment_start=segment.start_vert, segment_end=close_vertex)
            return new_segment
        else:
            return None

    # If the segment intersects an existing segment and is also close to an
    # existing vertex, we consider two different cases: Where the vertex is
    # part of the intersecting segment and not.
    elif vertex_is_close and intersecting_segment:
        # If the existing vertex is part of the intersecting segment, we
        # snap the end position of the new segment to the vertex.
        if (close_vertex is intersecting_segment.start_vert or 
            close_vertex is intersecting_segment.end_vert):
            if not avoid_duplicate:
                new_segment = Segment(segment_start=segment.start_vert, segment_end=close_vertex)
                return new_segment
            else:
                return None
        # If the existing vertex is not part of the intersecting segment, we
        # create a new intersection (and thus vertex) and split the existing
        # segment into two parts.
        else:
            return _create_intersection(segment, intersecting_segment, closest_value)
    # If no local constraints apply, and the segment does not break outer
    # bounds, we return it without alterations.
    else:
        return segment


def get_population_density_values(segment, population_image_array):
    return population_image_array[int(segment.end_vert.position[1])][int(segment.end_vert.position[0])]


# normalise pixel values to single value in range [0,1]
def normalise_pixel_values(image_array):
    return image_array[:,:,0] / 255
