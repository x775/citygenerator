# top down implementation of the Josauder implementation from github
# goal is to create a working minimal prototype
# refactoring and commenting should be done after implementation is done

# city size: 10.000 m x 10.000 m
# input image size: 1000x1000
# pixel size: 10 m x 10 m

import os
from queue import Queue
from input_setup import *
from enum import Enum
from growth_rules import *


class Rules(Enum):
    RULE_SEED = 1
    RULE_RADIAL = 2
    RULE_ORGANIC = 3
    RULE_GRID = 4
    RULE_MINOR = 5


def generate_roadmap(axiom):
    vertex_added_list = []
    vertex_front_queue = Queue(maxsize=0)
    rule_image_array = parse_image(os.getcwd() + "rule_image.png")
    population_image_array = normalise_pixel_values(parse_image(os.getcwd() + "population_image.png"))

    for vertex in axiom:
        vertex_added_list.extend(vertex)
        vertex_front_queue.put(vertex)

    # Iterate through the front queue, incrementally building the road network.
    while not vertex_front_queue.empty:
        current_vertex = vertex_front_queue.get()

        for suggested_vertex in generate_suggested_vertices(current_vertex, rule_image_array, population_image_array):
            continue #something


def generate_suggested_vertices(vertex, rule_image_array):
    suggested_vertices = []
    roadmap_rule = get_roadmap_rule(vertex, rule_image_array)
    population_density = get_population_density(vertex, population_image_array)

    if roadmap_rule == Rules.RULE_GRID:
        return grid(vertex, population_density)
    elif roadmap_rule == Rules.RULE_ORGANIC:
        # :)
    elif roadmap_rule == Rules.RULE_RADIAL:
        # :(
    elif roadmap_rule == Rules.RULE_SEED:
        # hehe
    else: #Rules.RULE_MINOR
    

#TODO:
# This assumes that the population density image has been converted to 
# black and white, and then all values for whiteness have been computed
# and normalised in the matrix. Thus, we only need to find the matching
# x,y for the vertex we are looking at.
def get_roadmap_rule(vertex, image_array):
    if vertex.seed:
        return Rules.RULE_SEED

    if vertex.is_major_road:
        # If we are dealing with a major road, we need to determine whether
        # we need to apply a radial, organic, or grid-based parttern.

        #TODO: Add support for other rules
        
        color = image_array[vertex.coordinates[0]][vertex.coordinates[1]]
        if color == (r,b,g,a):
            return Rules.RULE_GRID
        elif color == (r,b,g,a):
            return Rules.RULE_ORGANIC
        elif color == (r,b,g,a):
            return Rules.RULE_RADIAL

    else:
        return Rules.RULE_MINOR


def get_population_density_values(vertex, population_image_array):
    return population_image_array[vertex.coordinates[0]][vertex.coordinates[1]]


# normalise pixel values to single value in range [0,1]
def normalise_pixel_values(image_array):
    return image_array[:,:,0] / 255