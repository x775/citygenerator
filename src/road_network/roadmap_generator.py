# top down implementation of the Josauder implementation from github
# goal is to create a working minimal prototype
# refactoring and commenting should be done after implementation is done

# city size: 10.000 m x 10.000 m
# input image size: 1000x1000
# pixel size: 10 m x 10 m

import os
import json
import itertools
from queue import Queue
from enum import Enum
from scipy.spatial import cKDTree
import numpy as np
from segment import Segment
from input_setup import *
from growth_rules.grid import *
from helpers import *
from growth_rules.grid import *


class Rules(Enum):
    RULE_SEED = 1
    RULE_RADIAL = 2
    RULE_ORGANIC = 3
    RULE_GRID = 4
    RULE_MINOR = 5


def generate_roadmap(axiom):
    segment_added_list = []
    segment_front_queue = Queue(maxsize=0)
    rule_image_array = parse_image(os.getcwd() + "\\rule_image.png")
    population_image_array = normalise_pixel_values(parse_image(os.getcwd() + "\\population_density.png"))

    for segment in axiom:
        segment_added_list.append(segment)
        segment_front_queue.put(segment)

    # Iterate through the front queue, incrementally building the road network.
    max_iterations = 200
    i = 0
    while not segment_front_queue.empty() and i < max_iterations:
        current_segment = segment_front_queue.get()

        suggested_segments = generate_suggested_segments(current_segment, rule_image_array, population_image_array)
        verified_segments = verify_segments(suggested_segments, segment_added_list)
        
        for segment in verified_segments:
            segment_front_queue.put(segment)
        
        segment_added_list.extend(verified_segments)

        i += 1

        # check if segment is seed, if so, readd

    # Dump to json
    output = {}
    output['roadSegments'] = []
    output['roadVertices'] = []
    for segment in segment_added_list:
        output['roadVertices'].append({
            'position': {
                'x': float(segment.start_vert.position[0]),
                'y': float(segment.start_vert.position[1])
                }})
        output['roadVertices'].append({
            'position': {
                'x': float(segment.end_vert.position[0]),
                'y': float(segment.end_vert.position[1])
        }})
        output['roadSegments'].append({
            'startVertIndex': len(output['roadVertices']) - 2,
            'endVertIndex': len(output['roadVertices']) - 1
        })

    with open("roadnetwork.json", "w") as out:
        json.dump(output, out)
        

def generate_suggested_segments(segment, rule_image_array, population_image_array):
    roadmap_rule = get_roadmap_rule(segment, rule_image_array)
    population_density = get_population_density_values(segment, population_image_array)

    if roadmap_rule == Rules.RULE_GRID:
         suggested_segments = grid(segment, population_density)
    elif roadmap_rule == Rules.RULE_ORGANIC:
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

    return Rules.RULE_GRID

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
    

def verify_segments(suggested_segments, segment_added_list):
    # Check out of bounds
    # Check too close to existing
    # Check if intersect existing
    # Check if stops close to existing

    max_x = 1000 # hardcoded maximum x coordinate value
    max_y = 1000 # hardcoded maximum y coordinate value
    max_distance = 1 # hardcoded maximum distance that two vertices may be 

    segment_vertices = list(itertools.chain.from_iterable([[segment.start_vert.position, segment.end_vert.position] for segment in segment_added_list]))
    
    uniques = []
    for vertex in segment_vertices:
        if not any(np.array_equal(vertex, unique_vertex) for unique_vertex in uniques):
            uniques.append(vertex)
    # vertices_coordinates = list(set(segment_vertices))
    # vertices_coordinates = list(set([[vertex.position[0], vertex.position[1]] for vertex in segment_vertices]))
    
    vertex_tree = cKDTree(uniques)

    verified_segments = []

    for segment in suggested_segments:
        if segment.end_vert.position[0] > max_x or segment.end_vert.position[1] > max_y:
            continue # segment is not considered. I.e. not added to verified_segments
        
        _, result_index = vertex_tree.query(segment.end_vert.position, k=2, distance_upper_bound=max_distance)
        vertex_is_close = False

        # If no results are found, result_index will be length of vertices_coordinates.
        # if result_index < len(uniques):
        #     vertex_is_close = True

        if result_index[1] != len(uniques):
            result_index = result_index[1]
            vertex_is_close = True
            
        closest_value = np.inf
        intersecting_segment = None
        
        for old_segment in segment_added_list:
            intersection = compute_intersection(segment, old_segment)

            if(intersection[0] > 0.00001 and 
               intersection[0] < 0.99999 and 
               intersection[1] > 0.00001 and 
               intersection[1] < 0.99999 and 
               intersection[0] < closest_value):
                intersecting_segment = old_segment
                closest_value = intersection[0]
        
        if intersecting_segment and not vertex_is_close:
            segment_vector = (segment.end_vert.position - segment.start_vert.position)
            abs_intersection = intersection[0] * segment_vector + segment.start_vert.position
            new_segment = Segment(np.array([segment.start_vert.position, abs_intersection]))
            verified_segments.append(new_segment)
            
            intersecting_segment_old_end = intersecting_segment.end_vert
            # intersecting_segment.coordinates = np.array([intersecting_segment.start_vert.position, abs_intersection])
            intersecting_segment.end_vert = new_segment.end_vert

            old_segment_split = Segment.from_verts(new_segment.end_vert, intersecting_segment_old_end)
            segment_added_list.append(old_segment_split)
        elif vertex_is_close and not intersecting_segment:
            close_vertex_position = np.array(uniques[result_index])
            new_segment = Segment(np.array([segment.start_vert.position, close_vertex_position]))
            verified_segments.append(new_segment)
        elif vertex_is_close and intersecting_segment:
            close_vertex_position = np.array(uniques[result_index])
            
            if (np.array_equal(close_vertex_position, intersecting_segment.start_vert.position) or
                np.array_equal(close_vertex_position, intersecting_segment.end_vert.position)):
                new_segment = Segment(np.array([segment.start_vert.position, close_vertex_position]))
                verified_segments.append(new_segment)
            else:
                segment_vector = (segment.end_vert.position - segment.start_vert.position)
                abs_intersection = intersection[0] * segment_vector + segment.start_vert.position
                new_segment = Segment(np.array([segment.start_vert.position, abs_intersection]))
                verified_segments.append(new_segment)
            
                intersecting_segment_old_end = intersecting_segment.end_vert
                # intersecting_segment.coordinates = np.array([intersecting_segment.start_vert.position, abs_intersection])
                intersecting_segment.end_vert = new_segment.end_vert

                old_segment_split = Segment.from_verts(new_segment.end_vert, intersecting_segment_old_end)
                segment_added_list.append(old_segment_split)
        
        verified_segments.append(segment)
    
    return verified_segments

            

        # close, but not intersected; connect them
        # close, and intersected; connect at intersection
        # close, and intersected, and close to intersected vertex; connect them



def get_population_density_values(segment, population_image_array):
    return population_image_array[int(segment.end_vert.position[1])][int(segment.end_vert.position[0])]


# normalise pixel values to single value in range [0,1]
def normalise_pixel_values(image_array):
    return image_array[:,:,0] / 255


if __name__ == "__main__":
    random.seed(42)
    coords = np.array([[500,500], [505, 500]])
    axiom = Segment(coords)
    generate_roadmap([axiom])