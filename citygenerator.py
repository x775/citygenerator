from src.config_loader import ConfigLoader
from src.road_network.road_network_generator import generate_road_network

def generate(config_path):
    # step 0: load config
    config = ConfigLoader(config_path)
    road_network = generate_road_network(config)



# step 1: road network
# step 2: railroad network
# step 3: parcels
# step 4: buildings
# step 5: output 