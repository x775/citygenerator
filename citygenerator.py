import os
import time
import random
import numpy as np
from src.config_loader import ConfigLoader
from src.road_network.segment import Segment
from src.road_network.road_network_generator import generate_road_network
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt

def generate(config_path):
    # step 0: load config
    config = ConfigLoader(config_path)
    # step 1: road network
    road_network = generate_road_network(config)

    return road_network


if __name__ == "__main__":
    random.seed(42)
    t = time.process_time()
    road_network = generate(os.getcwd() + "/input/configs/test.json")
    segments_coords = [np.array([segment.start_vert.position, segment.end_vert.position]) for segment in road_network]
    lines = LineCollection(segments_coords)
    fig = plt.figure()

    ax = fig.add_subplot(1, 1, 1)
    ax.add_collection(lines)
    ax.autoscale()
    plt.show()

    print(time.process_time() - t)

# step 2: railroad network
# step 3: parcels
# step 4: buildings
# step 5: output 