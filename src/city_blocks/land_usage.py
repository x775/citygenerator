import math
import numpy as np
from matplotlib.path import Path
from shapely.geometry import Polygon
from src.utilities import read_tif_file

# INPUT:    List, numpy.Array
# OUTPUT:   List
# Create a meshgrid (rectangular grid of unique x and y values) based on the
# land_use_array shapes (matches the input image). Flatten each x and y arrays
# to one-dimensional arrays and take the transposed vstack (concatenate the
# first axis after 1-D arrays of shape (N,) have been reshaped to (1,N)).
# Iterate through all found polygons. For each polygon, find the positions for
# every vertex making up the polygon. Make a path combining every position. Make
# a bool array which is True if the path contains the corresponding point from
# the meshgrid using https://matplotlib.org/api/path_api.html#matplotlib.path.Path.contains_points.
# Return the indices from the mask and extract the inner coordinates. Convert
# these to a np.array and randomly sample N% of the coordinates making up the
# polygon. Extract the colour of each sampled coordinate against the
# land_use_array. The type of land use most common in the sample will be the
# type of land use assigned to the polygon. Meshgrid implementation inspired:
# by https://stackoverflow.com/a/45731214
def get_land_usage(polygons, config, N=2):
    size = max(config.land_use_array.shape[0], config.land_use_array.shape[1])
    x, y = np.meshgrid(np.arange(size), np.arange(size))
    x, y = x.flatten(), y.flatten()
    points = np.vstack((x, y)).T
    
    polygon_results = []
    for polygon in polygons:
        positions = [(int(round(vertex.position[0])), int(round(vertex.position[1]))) for vertex in polygon]
        path = Path(positions)
        grid = path.contains_points(points)
        mask = grid.reshape(size, size)
        indices = np.where(mask)

        inner_coords = np.array(list(zip(indices[1], indices[0])))

        if inner_coords.size == 0:
            continue

        random_indices = np.random.choice(inner_coords.shape[0], math.ceil(len(inner_coords) / N), replace=False)
        random_coords = inner_coords[random_indices]
        
        land_usages = {
            "residential" : 0,
            "commercial" : 0,
            "industry" : 0,
        }

        # get the land use in the sampled coordinates
        for coord in random_coords:
            sample = config.land_use_array[coord[1]][coord[0]]
            if sample in config.residential_legends:
                land_usages["residential"] += 1
            elif sample in config.commercial_legends:
                land_usages["commercial"] += 1
            elif sample in config.industry_legends:
                land_usages["industry"] += 1
        
        # determine land use based on the most common observed land use in the samples
        final_use = max(land_usages, key=land_usages.get)
        if land_usages[final_use] == 0:
            final_use = "none"

        density = get_population_density(random_coords, config.population_density_array)
        population = get_population(config.pixel_scaling_factor, density, positions)

        polygon_results.append({"polygon" : [{'x': float(vertex.position[0]), 'z': float(vertex.position[1]), 'mark': 0} for vertex in polygon], 
                                "land_usage" : final_use, "population_density" : density, "population" : population})

    return polygon_results


# INPUT:    List, Config
# OUTPUT:   List
# Return the average population density for the given polygon.
def get_population_density(indices, population_density_array):
    population_density = []
    for index in indices:
        density = population_density_array[index[1], index[0]]
        population_density.append(density)

    # Return the average population density.
    return sum(population_density) / len(population_density)


# INPUT:    Float, List
# OUTPUT:   Integer
# Return the corresponding population given positions of a polygon w/ density.
# Shapely.Polygon.area assumes list of vertices is in clockwise or
# anti-clockwise manner. 
def get_population(scale, density, positions):
    scaled_positions = [(position[0] * scale, position[1] * scale) for position in positions]
    area = Polygon(scaled_positions).area
    return math.ceil(density * area)
