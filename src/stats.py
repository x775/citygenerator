import math
import numpy as np
import matplotlib.pyplot as plt

NUM_BINS = 36

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

def compute_orientation_entropy(orientation_histogram):
    pass

def compute_orientation_order(orientation_entropy):
    pass

def show_orientation_histogram(orientation_histogram):
    # Calculate bin centers
    bin_width = 2*math.pi / NUM_BINS
    centers = np.arange(0, 2*math.pi, bin_width)

    # Plot polar histogram
    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(111, projection='polar')
    ax.bar(centers, orientation_histogram, width=bin_width, bottom=0.0, color='.8', edgecolor='k')
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    plt.show()
