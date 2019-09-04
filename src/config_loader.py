import os
import json
import numpy as np
from src.utilities import parse_image
from src.road_network.segment import Segment

class ConfigLoader:
    def __init__(self, config_path=None):
        
        try:
            with open(config_path, "r") as config_file:
                for key, value in json.loads(config_file).items():
                    setattr(self, key, value["value"])
        except FileNotFoundError:
            print("Incorrect or missing config file!")
            #break

        # Call all generation functions
        self.init_road_network()


    def init_road_network(self):
        # Create starting segments based on config axiom.
        self.axiom = [Segment(np.array(segment_coordinates)) for segment_coordinates in self.axiom]

        # Parse road rule map and population density map.
        path = "../input/images/"
        self.road_rules_array = parse_image(path + self.rule_image_name)
        self.population_density_array = parse_image(path + self.population_density_image_name)