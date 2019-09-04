import numpy as np

# INPUT:    numpy.Array, int/float
# OUTPUT:   numpy.Array
# rotates a vector around its starting point
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