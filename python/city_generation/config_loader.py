import os
import json

class ConfigLoader:
    def __init__(self, config=None):
        directory = os.getcwd()

        try:
            with open(directory + "/configs/" + config + ".json", "r") as config_file:
                for key, value in json.loads(config_file).items():
                    setattr(self, key, value["value"])
        except FileNotFoundError:
            print("Incorrect or missing config file!")

        self.maxLength = max(self.radiallMax, self.gridlMax, self.organiclMax,
                            self.minor_roadlMax, self.seedlMax)