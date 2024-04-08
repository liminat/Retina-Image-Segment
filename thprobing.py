
# This script is used for implement thrshlhold probing of matched filter response
# generated by mfr.py

# The input image is matched filter reponse with Gaussian filter. 
# The output file is the binary image after thresholded by probes. 

import numpy as np
import cv2
import sys
import timeit
import copy as cp
import os

def inbounds(shape, indices):
    '''
    Test if the given coordinates inside the given image. 

    The first input parameter is the shape of image (height, weight) and the 
    second parameter is the coordinates to be tested (y, x)

    The function returns True if the coordinates inside the image and vice versa.

    '''
    assert len(shape) == len(indices)
    for i, ind in enumerate(indices):
        if ind < 0 or ind >= shape[i]:
            return False
    return True