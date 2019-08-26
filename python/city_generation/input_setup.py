import numpy as np
from PIL import Image


# INPUT: name of image file
# OUTPUT: 3d array of color values (r,g,b,a)
def parse_image(filename):
    # We open the supplied image and convert it to a numpy array.
    # dtype is inferred as uint8, and the output is an array of
    # lists where each parent list corresponds to a row of pixel
    # values. All pixels contain [r, g, b, a]-values.
    return np.asarray(Image.open(filename))


# INPUT: 3d array of color values (r,g,b,a)
#        color to find coordinates of (r,g,b,a)
# OUTPUT: 2d array of coordinates of pixels with given color
def find_legend_color_coordinates(image_arr, legend_color):
    # Given an array of colour values, and a specific legend color,
    # we create and subsequently zip a 2-tuple of arrays containing 
    # indices in the first and second dimension corresponding to the 
    # pixel values of the colour matching the legend.
    indices = np.where(np.all(image_arr == legend_color, axis=-1))
    # Convert iterator to list to array before returning.
    return np.array(list(zip(indices[0], indices[1]))) 


# INPUT: 2d array of coordinates
# OUTPUT: x and y tuple for centroid
def find_coordinates_centroid(coordinates):
    # Given an array of coordinates, we find the centroid
    # of the coordinates and returns them as a tuple.
    coordinate_length = coordinates.shape[0]
    coordinate_x_sum = np.sum(coordinates[:, 0])
    coordinate_y_sum = np.sum(coordinates[:, 1])
    return (coordinate_x_sum / coordinate_length, coordinate_y_sum / coordinate_length)


def find_radial_rule_centers(image_arr, legend_color):
    indices = find_legend_color_coordinates(image_arr, legend_color)
    return find_coordinates_centroid(indices)



# TODO: implement clustering for multiple clusters of same legend color