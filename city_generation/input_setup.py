import numpy as np
from PIL import Image

def parse_image(filename):
    # We open the supplied image and convert it to a numpy array.
    # dtype is inferred as uint8, and the output is an array of 
    # lists where each parent list corresponds to a row of pixel
    # values. All pixels contain [r, g, b, a]-values.
    return np.asarray(Image.open(filename))