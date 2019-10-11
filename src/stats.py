import math
import numpy as np
import matplotlib.pyplot as plt

NUM_BINS = 36

# This is the average degree of the graph vertices for a simplified graph containing only
# intersections and dead ends.
# Metric taken from https://appliednetsci.springeropen.com/articles/10.1007/s41109-019-0189-1
def compute_average_node_degree(vertex_dict):
    node_sum = 0
    degree_sum = 0
    for _, road_segments in vertex_dict.items():
        # Ignore straights and bends
        if len(road_segments) == 2:
            continue
        
        degree_sum += len(road_segments)
        node_sum += 1
    return degree_sum / node_sum

# Counts the number of intersections in the road network
def compute_intersection_count(vertex_dict):
    node_sum = 0
    for _, road_segments in vertex_dict.items():
        # Ignore straights, bends and dead ends
        if len(road_segments) <= 2:
            continue
        
        node_sum += 1
    return node_sum

# The is the proportion of 3-way intersections with respect to the simplified graph containing only
# intersections and dead ends.
def compute_proportion_3way_intersections(vertex_dict):
    node_sum = 0
    three_way_sum = 0
    for _, road_segments in vertex_dict.items():
        # Ignore straights and bends
        if len(road_segments) == 2:
            continue
        
        # Count if 4-way intersection
        if len(road_segments) == 3:
            three_way_sum += 1
        node_sum += 1
    return three_way_sum / node_sum

# The is the proportion of 4-way intersections with respect to the simplified graph containing only
# intersections and dead ends.
# Metric taken from https://appliednetsci.springeropen.com/articles/10.1007/s41109-019-0189-1
def compute_proportion_4way_intersections(vertex_dict):
    node_sum = 0
    four_way_sum = 0
    for _, road_segments in vertex_dict.items():
        # Ignore straights and bends
        if len(road_segments) == 2:
            continue
        
        # Count if 4-way intersection
        if len(road_segments) == 4:
            four_way_sum += 1
        node_sum += 1
    return four_way_sum / node_sum

# The is the proportion of dead-ends with respect to the simplified graph containing only
# intersections and dead-ends.
# Metric taken from https://appliednetsci.springeropen.com/articles/10.1007/s41109-019-0189-1
def compute_proportion_dead_ends(vertex_dict):
    node_sum = 0
    dead_end_sum = 0
    for _, road_segments in vertex_dict.items():
        # Ignore straights and bends
        if len(road_segments) == 2:
            continue
        
        # Count if dead-end
        if len(road_segments) == 1:
            dead_end_sum += 1
        node_sum += 1
    return dead_end_sum / node_sum

# Sums the road length of all road segments in the graph
def compute_total_road_length(road_segments, config=None, pixel_scaling_factor=None):
    if config is None and pixel_scaling_factor is None:
        raise ValueError("One of config or pixel_scaling_factor parameters must be set")

    if config is not None:
        pixel_scaling_factor = config.pixel_scaling_factor

    length_sum = 0
    for road_segment in road_segments:
        road_vector = road_segment.end_vert.position - road_segment.start_vert.position
        road_length = np.linalg.norm(road_vector) * pixel_scaling_factor
        length_sum += road_length
    return length_sum

# Metric taken from https://appliednetsci.springeropen.com/articles/10.1007/s41109-019-0189-1
def compute_orientation_histogram(road_segments):
    histogram = [0 for i in range(NUM_BINS)] # Zero all bins
    for road_segment in road_segments:
        # Calculate orientations in both directions along the road
        road_vector = road_segment.end_vert.position - road_segment.start_vert.position
        road_length = np.linalg.norm(road_vector)
        theta_forward = (2*math.pi + math.atan2(road_vector[1], road_vector[0])) % (2*math.pi)
        theta_backward = (2*math.pi + theta_forward + math.pi) % (2*math.pi) # Add 180 degrees to get reverse angle

        # Calculate the two bins the road falls into based on orientation
        center_adjust = (2*math.pi / NUM_BINS) / 2
        bin_forward = int((NUM_BINS + (theta_forward + center_adjust) / (2*math.pi / NUM_BINS)) % NUM_BINS)
        bin_backward = int((NUM_BINS + (theta_backward + center_adjust) / (2*math.pi / NUM_BINS)) % NUM_BINS)

        # Add segment weight to bins, using road length as weights (shorter road segments are given less weight)
        histogram[bin_forward] += road_length
        histogram[bin_backward] += road_length
    return histogram

# Metric formula taken from: https://appliednetsci.springeropen.com/articles/10.1007/s41109-019-0189-1
def compute_orientation_entropy(orientation_histogram):
    # Compute normalized histogram (each bin value represents the proporation of orientations that fall in that bin)
    sum = 0
    for bin in orientation_histogram:
        sum += bin
    norm_histogram = orientation_histogram / sum

    entropy = 0
    for proportion in norm_histogram:
        entropy -= proportion * math.log(proportion + 1e-8)

    return entropy

# Metric formula taken from: https://appliednetsci.springeropen.com/articles/10.1007/s41109-019-0189-1
# INPUT: Orientation entropy (float)
# OUPUT: Orientation order (float) - (0, 1) from perfectly uniform to idealized four-way grid
def compute_orientation_order(orientation_entropy):
    min_entropy = -0.25 * math.log(0.25) * 4 # Perfect grid
    max_entropy = math.log(NUM_BINS) # Perfectly uniform distribution of street bearings
    orientation_order = 1 - ((orientation_entropy - min_entropy) / (max_entropy - min_entropy)) ** 2
    return orientation_order

# Displays the polar histogram of road orientations
# y axis going from top to bottom, so angles go clockwise (theta_direction=-1) by default
def show_orientation_histogram(orientation_histogram, theta_direction=-1):
    # Calculate bin centers
    bin_width = 2*math.pi / NUM_BINS
    centers = np.arange(0, 2*math.pi, bin_width)

    # Plot polar histogram
    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(111, projection='polar')
    ax.set_yticklabels([])
    ax.bar(centers, orientation_histogram, width=bin_width, bottom=0.0, color='.8', edgecolor='k')
    ax.set_theta_direction(theta_direction) # y axis going from top to bottom, so angles go clockwise by default
    if theta_direction > 0:
        ax.set_thetagrids(range(0, 360, 45), ('E', '', 'N', '', 'W', '', 'S'))
    else:
        ax.set_thetagrids(range(360, 0, -45), ('E', '', 'N', '', 'W', '', 'S'))
    plt.show()
