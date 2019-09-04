import os
import time
import random
import numpy as np
from src.config_loader import ConfigLoader
from src.road_network.segment import Segment
from src.road_network.road_network_generator import generate_road_network

def generate(config_path):
    # step 0: load config
    config = ConfigLoader(config_path)
    # step 1: road network
    road_network = generate_road_network(config)

    return road_network


if __name__ == "__main__":
    random.seed(42)
    t = time.process_time()
    print(len(generate(os.getcwd() + "/input/configs/test.json")))
    print(time.process_time() - t)

# step 2: railroad network
# step 3: parcels
# step 4: buildings
# step 5: output 