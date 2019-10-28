import os
import json
import numpy as np
from src.utilities import parse_image
from src.utilities import read_tif_file
from src.utilities import find_legend_centers
from src.utilities import find_legend_color_coordinates
from src.road_network.segment import Segment

class ConfigLoader:
    def __init__(self, config_path=None):
        
        try:
            with open(config_path, "r") as config_file:
                for key, value in json.load(config_file).items():
                    setattr(self, key, value["value"])
        except FileNotFoundError:
            print("Incorrect or missing config file!")
            #break

        # Create starting segments based on config axiom.
        self.axiom = [Segment(segment_array=np.array(segment_coordinates)) for segment_coordinates in self.axiom]

        # Parse road rule map and population density map.
        path = os.getcwd() + "/input/images/"
        self.road_rules_array = parse_image(path + self.rule_image_name)
        self.population_density_array = read_tif_file(path + self.population_density_image_name)
        # find radial centers. Only relevant if radial road rule is used.
        self.radial_centers = find_legend_centers(self.road_rules_array, self.radial_legend)
        # Parse water map.
        self.water_map_array = parse_image(path + self.water_map_image_name)
        # Parse land usage map.
        self.land_use_array = read_tif_file(path + self.land_use_image_name)
