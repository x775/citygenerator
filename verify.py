import math
import geojson
import numpy as np
import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt

ox.config(log_console=True, use_cache=True)
weight_by_length = False

# Grab Auckland matching the bbox we are using.
Auckland = ox.graph_from_bbox(-36.83, -36.94, 174.82, 174.68, network_type='drive')

# Extract road_segments and vertex_dict.
vertex_dict = {}
road_segments = []

for edge in Auckland.edges:
    start_id, end_id, _ = edge
    start_vert = (Auckland.nodes[start_id]["x"], Auckland.nodes[start_id]["y"])
    end_vert = (Auckland.nodes[end_id]["x"], Auckland.nodes[end_id]["y"])
    road_segments.append((start_vert, end_vert))
    
    if start_vert in vertex_dict:
        if (start_vert, end_vert) not in vertex_dict[start_vert]:
            vertex_dict[start_vert].append((start_vert, end_vert))
    else:
        vertex_dict[start_vert] = [(start_vert, end_vert)]

    if end_vert in vertex_dict:
        if (start_vert, end_vert) not in vertex_dict[end_vert]:
            vertex_dict[end_vert].append((start_vert, end_vert))
    else:
        vertex_dict[end_vert] = [(start_vert, end_vert)]

# Import and re-use statistic functions.
from src.stats import compute_total_road_length
from src.stats import compute_intersection_count
from src.stats import compute_average_node_degree
from src.stats import compute_proportion_dead_ends
from src.stats import compute_proportion_3way_intersections
from src.stats import compute_proportion_4way_intersections

# Reimplement histogram orientation to match new format.

def compute_orientation_histogram(road_segments):
    histogram = [0 for i in range(NUM_BINS)] # Zero all bins
    for road_segment in road_segments:
        # Calculate orientations in both directions along the road
        segment = np.array(road_segment)
        road_vector = segment[1] - segment[0]
        road_length = np.linalg.norm(road_vector)
        theta_forward = (2*math.pi + math.atan2(road_vector[1], road_vector[0])) % (2*math.pi)
        theta_backward = (2*math.pi + theta_forward + math.pi) % (2*math.pi) # Add 180 degrees to get reverse angle

        # Calculate the two bins the road falls into based on orientation
        center_adjust = (2*math.pi / NUM_BINS) / 2
        bin_forward = int((NUM_BINS + (theta_forward + center_adjust) / (2*math.pi / NUM_BINS)) % NUM_BINS)
        bin_backward = int((NUM_BINS + (theta_backward + center_adjust) / (2*math.pi / NUM_BINS)) % NUM_BINS)

        # Add segment weight to bins, using road length as weights (shorter road segments are given less weight)
        histogram[bin_forward] += road_length
        histogram[bin_backward] += road_length
    return histogram

# Import remaining existing histogram functions.
from src.stats import compute_orientation_order
from src.stats import compute_orientation_entropy
from src.stats import show_orientation_histogram

# Call everything.

orientation_histogram = compute_orientation_histogram(road_segments)
entropy = compute_orientation_entropy(orientation_histogram)
orientation_order = compute_orientation_order(entropy)
avg_node_degree = compute_average_node_degree(vertex_dict)
proportion_dead_ends = compute_proportion_dead_ends(vertex_dict)
proportion_3way_intersections = compute_proportion_3way_intersections(vertex_dict)
proportion_4way_intersections = compute_proportion_4way_intersections(vertex_dict)
intersection_count = compute_intersection_count(vertex_dict)
total_road_length = compute_total_road_length(road_segments)

print('Entropy:', entropy)
print('Orientation-Order:', orientation_order)
print('Average Node Degree:', avg_node_degree)
print('Proportion Dead-Ends:', proportion_dead_ends)
print('Proportion 3-way Intersections', proportion_3way_intersections)
print('Proportion 4-way Intersections', proportion_4way_intersections)
print('Intersection Count:', intersection_count)
print('Total Road Length:', total_road_length)

# Check with OSMNX statistics as well.
ox.basic_stats(Auckland)

# Print orientation histogram.
show_orientation_histogram(orientation_histogram)