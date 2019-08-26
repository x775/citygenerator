import numpy as np
import pandas as pd
from PIL import Image


def parse_image(filename):
    # We open the supplied image and convert it to a numpy array.
    # dtype is inferred as uint8, and the output is an array of 
    # lists where each parent list corresponds to a row of pixel
    # values. All pixels contain [r, g, b, a]-values.
    return np.asarray(Image.open(filename))
    
    
def count_occurrences(array):
    unique, counts = np.unique(array, return_counts=True)
    return np.asarray((unique,counts)).T

t = parse_image("testshot.png")
c = count_occurrences(t)



print(c)