import os
import time
import random
import numpy as np
from src.config_loader import ConfigLoader
from src.road_network.segment import Segment
from src.road_network.road_network_generator import generate_road_network
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
import src.city_blocks.polygons as polygons
import src.city_blocks.land_usage as land_usage

def generate(config_path):
    # step 0: load config
    config = ConfigLoader(config_path)
    # step 1: road network
    road_network, vertex_dict = generate_road_network(config)
    # step 2: polygons
    polys = polygons.get_polygons(vertex_dict)
    del polys[0] # we delete the first polygon found as it is always the outside area
    # step 3: land use
    land_usages = land_usage.get_land_usage(polys, config)

    return config.water_map_array, road_network, land_usages


if __name__ == "__main__":
    random.seed(41)
    t = time.process_time()
    water_map_array, road_network, land_usages = generate(os.getcwd() + "/input/configs/test.json")
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
            x_coords.append(vertex.position[0])
            y_coords.append(vertex.position[1])
        ax.fill(x_coords, y_coords, color)

    ax.autoscale()
    print(time.process_time() - t)
    plt.show()
