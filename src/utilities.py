import numpy as np
from PIL import Image
import skimage.morphology
import gdal

# INPUT:    String
# OUTPUT:   numpy.Array
# We open the supplied image and convert it to a numpy array.
# dtype is inferred as uint8, and the output is an array of
# lists where each parent list corresponds to a row of pixel
# values. All pixels contain [r, g, b]-values.
def parse_image(filename):
    image_array = np.asarray(Image.open(filename))
    # Remove alpha value if image only contains a single color.
    if image_array.shape[2] == 4:
        image_array = np.delete(image_array, 3, 2)
    return image_array


# INPUT:    numpy.Array, numpy.Array
# OUTPUT:   numpy.Array
# Given an array of colour values, and a specific legend color,
# we create and subsequently zip a 2-tuple of arrays containing 
# indices in the first and second dimension corresponding to the 
# pixel values of the colour matching the legend.
def find_legend_color_coordinates(image_array, legend_color):
    indices = np.where(np.all(image_array == legend_color, axis=-1))
    # Convert iterator to list to array before returning.
    return np.array(list(zip(indices[0], indices[1]))) 


# INPUT:    Segment
# OUTPUT:   numpy.Array (RGB value)
def find_pixel_value(segment, image_array):
    y = int(round(segment.end_vert.position[1]))
    x = int(round(segment.end_vert.position[0]))
    return image_array[y,x]


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
#OUTPUT:    numpy.Array
def find_legend_centers(image_array, legend):
    # Find all coordinates matching the specified legend.
    legend_indices = find_legend_color_coordinates(image_array, legend)

    # if the legend is not present in the image, return an empty list, i.e. no centers
    if legend_indices.size == 0:
        return []
    
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

    return np.array(centroids)


# INPUT:    numpy.Array, Float
# OUTPUT:   numpy.Array
def rotate(vector, angle):

    # Often used special case
    if angle == 90:
        return np.array([-vector[1], vector[0]])
    
    angle = angle * np.pi / 180
    rotation_matrix = np.array([np.cos(angle), np.sin(angle), -np.sin(angle), np.cos(angle)]).reshape(2,2)
    
    return np.dot(vector, rotation_matrix)


# INPUT:    Segment, Segment
# OUTPUT:   numpy.Array
# Computes the normalised position of the intersection on segment_one.
def compute_intersection(segment_one, segment_two):
    segment_one_start = segment_one.start_vert.position
    segment_one_sub = segment_one.end_vert.position - segment_one.start_vert.position
    segment_two_start = segment_two.start_vert.position
    segment_two_sub = segment_two.end_vert.position - segment_two.start_vert.position
    
    try:
        return np.linalg.solve(np.array([segment_one_sub, -segment_two_sub]).T, segment_two_start - segment_one_start)
    except np.linalg.linalg.LinAlgError:
        return np.array([np.inf, np.inf])


# INPUT:    Segment, np.Array
# OUTPUT:   Integer
# Get the population density value for a specific pixel of
# the population density image
def get_population_density_values(segment, population_image_array):
    return population_image_array[int(segment.end_vert.position[1])][int(segment.end_vert.position[0])]


# INPUT:    numpy.Array
# OUTPUT:   numpy.Array
# normalise pixel values to single value in range [0,1]
def normalise_pixel_values(image_array):
    return image_array[:,:,0] / 255


# INPUT:    String
# OUTPUT:   numpy.Array
import gdal
def read_tif_file(filename):
    gdo = gdal.Open(filename)
    band = gdo.GetRasterBand(1)
    return np.array(gdo.ReadAsArray(0, 0, band.XSize, band.YSize))
