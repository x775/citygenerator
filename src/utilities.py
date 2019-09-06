import numpy as np
from PIL import Image
import skimage.morphology

# INPUT:    String
# OUTPUT:   numpy.Array
def parse_image(filename):
    # We open the supplied image and convert it to a numpy array.
    # dtype is inferred as uint8, and the output is an array of
    # lists where each parent list corresponds to a row of pixel
    # values. All pixels contain [r, g, b, a]-values.
    return np.asarray(Image.open(filename))


# INPUT:    numpy.Array, numpy.Array
# OUTPUT:   numpy.Array
def find_legend_color_coordinates(image_arr, legend_color):
    # Given an array of colour values, and a specific legend color,
    # we create and subsequently zip a 2-tuple of arrays containing 
    # indices in the first and second dimension corresponding to the 
    # pixel values of the colour matching the legend.
    indices = np.where(np.all(image_arr == legend_color, axis=-1))
    # Convert iterator to list to array before returning.
    return np.array(list(zip(indices[0], indices[1]))) 


# INPUT:    numpy.Array
# OUTPUT:   Tuple
def find_coordinates_centroid(coordinates):
    # Given an array of coordinates, we find the centroid
    # of the coordinates and returns them as a tuple.
    coordinate_length = coordinates.shape[0]
    coordinate_x_sum = np.sum(coordinates[:, 0])
    coordinate_y_sum = np.sum(coordinates[:, 1])
    return (coordinate_x_sum / coordinate_length, coordinate_y_sum / coordinate_length)


#INPUT:     numpy.Array, List
#OUTPUT:    List
def find_legend_centers(image_array, legend):
    # Find all coordinates matching the specified legend.
    legend_indices = find_legend_color_coordinates(image_array, legend)
    
    # Create a Boolean matrix of size image_width x image_height and mark every
    # cell as either True or False depending on whether the legend colour is
    # present in that pixel. 
    legend_matches = np.zeros((np.shape(image_array)[0], np.shape(image_array)[1]), dtype=bool)
    legend_matches[legend_indices[:,0], legend_indices[:,1]] = True

    # Find clusters of the legend in the array and label them.
    labeled_matches = skimage.morphology.label(legend_matches)

    # Create list of coordinates for each cluster in the array.
    clusters = [list(zip(y, x)) for y, x in 
               [(labeled_matches == cluster).nonzero() for cluster in range(1, labeled_matches.max()+1)]]
               
    # Find the centroids of each cluster.
    centroids = [find_coordinates_centroid(coords) for coords in np.array(clusters)]

    return centroids