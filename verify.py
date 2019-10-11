import math
import geojson
import numpy as np
import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt
from src.road_network.vertex import Vertex
from src.road_network.segment import Segment
from src.config_loader import ConfigLoader
from citygenerator import visualise

# Import and re-use statistic functions.
from src.stats import compute_total_road_length
from src.stats import compute_intersection_count
from src.stats import compute_proportion_dead_ends
from src.stats import compute_proportion_3way_intersections
from src.stats import compute_proportion_4way_intersections
from src.stats import compute_orientation_histogram
from src.stats import compute_orientation_order
from src.stats import compute_orientation_entropy
from src.stats import show_orientation_histogram

config = ConfigLoader('input/configs/auckland.json')
ox.config(log_console=True, use_cache=True)
weight_by_length = False
NUM_BINS = 36

# Grab Auckland matching the bbox we are using.
Auckland = ox.graph_from_bbox(-36.83, -36.94, 174.82, 174.68, network_type='drive')

# Extract road_segments and vertex_dict.
vertex_dict = {}
road_segments = []

for edge in Auckland.edges:
    start_id, end_id, _ = edge
    start_vert = Vertex(np.array((Auckland.nodes[start_id]["x"], Auckland.nodes[start_id]["y"])))
    end_vert = Vertex(np.array((Auckland.nodes[end_id]["x"], Auckland.nodes[end_id]["y"])))
    road_segment = Segment(start_vert, end_vert)
    road_segments.append(road_segment)
    
    if start_vert in vertex_dict:
        if road_segment not in vertex_dict[start_vert]:
            vertex_dict[start_vert].append(road_segment)
    else:
        vertex_dict[start_vert] = [road_segment]

    if end_vert in vertex_dict:
        if road_segment not in vertex_dict[end_vert]:
            vertex_dict[end_vert].append(road_segment)
    else:
        vertex_dict[end_vert] = [road_segment]

# Call everything.
orientation_histogram = compute_orientation_histogram(road_segments)
entropy = compute_orientation_entropy(orientation_histogram)
orientation_order = compute_orientation_order(entropy)
proportion_dead_ends = compute_proportion_dead_ends(vertex_dict)
proportion_3way_intersections = compute_proportion_3way_intersections(vertex_dict)
proportion_4way_intersections = compute_proportion_4way_intersections(vertex_dict)
intersection_count = compute_intersection_count(vertex_dict)
total_road_length = ox.basic_stats(Auckland)["street_length_total"]
avg_node_degree = ox.basic_stats(Auckland)["streets_per_node_avg"]

print('Entropy:', entropy)
print('Orientation-Order:', orientation_order)
print('Average Node Degree:', avg_node_degree)
print('Proportion Dead-Ends:', proportion_dead_ends)
print('Proportion 3-way Intersections', proportion_3way_intersections)
print('Proportion 4-way Intersections', proportion_4way_intersections)
print('Intersection Count:', intersection_count)
print('Total Road Length:', total_road_length)

# visualise(config.water_map_array, road_segments)

# Print orientation histogram.
show_orientation_histogram(orientation_histogram, theta_direction=1)