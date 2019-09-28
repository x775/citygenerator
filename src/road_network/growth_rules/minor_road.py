import random
import numpy as np
from src.utilities import rotate
from src.road_network.vertex import Vertex
from src.road_network.segment import Segment
from src.road_network.growth_rules.grid import grid
from src.road_network.growth_rules.organic import organic

def minor_road(config, segment):
    road_organic_probability = config.minor_road_organic_probability

    if random.uniform(0,1) <= road_organic_probability:
        return organic(config,segment, 1.5)
    else:
        return grid(config, segment, 1.5)
