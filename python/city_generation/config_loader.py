import os
import json
import numpy as np
from input_setup import *
from roadmap_generation.vertex import Vertex

class ConfigLoader:
    def __init__(self, config=None):
        directory = os.getcwd()
        
        try:
            with open(directory + "/configs/" + config + ".json", "r") as config_file:
                for key, value in json.loads(config_file).items():
                    setattr(self, key, value["value"])
        except FileNotFoundError:
            print("Incorrect or missing config file!")
            #break

        # Call all generation functions
        self.init_road_network()


    def init_road_network(self):

        self.maxLength = max(self.radiallMax, self.gridlMax, self.organiclMax,
                            self.minor_roadlMax, self.seedlMax)
        
        # Create initial list of starter Vertex-objects as supplied in config.
        self.axiom = [Vertex(np.array([coordinate[0], coordinate[1]])) for coordinate in self.axiom]

        # Parse road rule map and population density map.
        self.road_rules = parse_image(self.road_rule_path)
        self.population_density = parse_image(self.population_density_path)

        # Find city centers based on population density
        self.city_centers = find_legend_color_coordinates(self.population_density, self.population_density_legend)

        # Find radial rule centers
        # TODO: currently only works for a single radial pattern
        self.radial_rule_centers = find_coordinates_centroid(self.road_rules, self.road_rules_legend)
            
    


"""
Config file should contain

* one config file per city; contains all input
* list of relevant legends for input images
* list of population density segmentations (last in list = highest density)


"""