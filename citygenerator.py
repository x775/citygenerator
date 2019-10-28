import os
import time
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from src.to_json import city_to_json
from src.config_loader import ConfigLoader
from src.road_network.segment import Segment
from src.road_network.road_network_generator import generate_road_network
import src.city_blocks.polygons as polygons
import src.city_blocks.land_usage as land_usage
from src.stats import compute_orientation_histogram, show_orientation_histogram
from src.stats import compute_orientation_entropy, compute_orientation_order
from src.stats import compute_average_node_degree, compute_intersection_count, compute_total_road_length
from src.stats import compute_proportion_3way_intersections, compute_proportion_4way_intersections, compute_proportion_dead_ends


# INPUT:    String, (Bool, Bool)
# OUTPUT:   Generated city (visualisation)
# Main function used to generate an intermediate representation of a city.
# If show_city is true, the representation is visualised using matplotlib.
# If show_time is true, the process time required to generate the intermediate representation is shown.
# If show_stats is true, the statistics used to evaluate the representation are shown
def generate(config_path, show_city=False, show_time=False, show_stats=False):
    if show_time:
        t = time.process_time()

    # Step 0: Load config.
    config = ConfigLoader(config_path)
    # Step 1: Grow road network.
    road_network, vertex_dict = generate_road_network(config)
    # Step 2: Compute polygons based on road network.
    polys = polygons.get_polygons(vertex_dict)
    del polys[0] # We delete the first polygon as this corresponds to the outer area.
    # Step 3: Determine land usages.
    land_usages = land_usage.get_land_usage(polys, config)
    # Step 4: Dump to .json.
    city_to_json(road_network, list(vertex_dict.keys()), land_usages)

    if show_time:
        print('Time:', time.process_time() - t)

    if show_stats:
        orientation_histogram = compute_orientation_histogram(road_network)
        entropy = compute_orientation_entropy(orientation_histogram)
        orientation_order = compute_orientation_order(entropy)
        avg_node_degree = compute_average_node_degree(vertex_dict)
        proportion_dead_ends = compute_proportion_dead_ends(vertex_dict)
        proportion_3way_intersections = compute_proportion_3way_intersections(vertex_dict)
        proportion_4way_intersections = compute_proportion_4way_intersections(vertex_dict)
        intersection_count = compute_intersection_count(vertex_dict)
        total_road_length = compute_total_road_length(road_network, config=config)

        print('Entropy:', entropy)
        print('Orientation-Order:', orientation_order)
        print('Average Node Degree:', avg_node_degree)
        print('Proportion Dead-Ends:', proportion_dead_ends)
        print('Proportion 3-way Intersections', proportion_3way_intersections)
        print('Proportion 4-way Intersections', proportion_4way_intersections)
        print('Intersection Count:', intersection_count)
        print('Total Road Length:', total_road_length)

    if show_city:
        visualise(config.water_map_array, road_network, land_usages=land_usages)

    if show_stats:
        show_orientation_histogram(orientation_histogram)


# INPUT:    numpy.Array, List, Dict
# OUTPUT:   matplotlib plot
# Function used to visualise intermediate representation using matplotlib
def visualise(water_map_array, road_network, land_usages=None):
    major_segment_coords = [np.array([segment.start_vert.position, segment.end_vert.position]) for segment in road_network 
                            if not segment.is_minor_road]
    minor_segment_coords = [np.array([segment.start_vert.position, segment.end_vert.position]) for segment in road_network 
                            if segment.is_minor_road]
    major_lines = LineCollection(major_segment_coords)
    minor_lines = LineCollection(minor_segment_coords, linewidths=[0.6], colors=[[0, 0, 0, 0.8]])
    fig = plt.figure()

    ax = fig.add_subplot(1, 1, 1)
    ax.imshow(water_map_array)
    ax.add_collection(major_lines)
    ax.add_collection(minor_lines)

    if land_usages is not None:
        for use in land_usages:
            x_coords = []
            y_coords = []
            poly = use["polygon"]
            if use["land_usage"] == "residential":
                color = "purple"
            elif use["land_usage"] == "commercial":
                color = "y"
            elif use["land_usage"] == "industry":
                color = "b"
            else:
                color = "r"

            for vertex in poly:
                x_coords.append(vertex['x'])
                y_coords.append(vertex['z'])
            ax.fill(x_coords, y_coords, color)

    ax.autoscale()
    plt.show()


if __name__ == "__main__":
    random.seed(42)
    generate(os.getcwd() + "/input/configs/auckland.json", show_city=True, show_time=True, show_stats=True)
