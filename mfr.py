

# This script is to generate mathched filter response with both Gaussian function and 
# first-order derivatie of Gaussian function. 

# The input files are original color image and its mark image. The out put files are 
# matched filter response with Gaussian filter (grayscale image, H+name.tiff) and the image 
# threshold with matched filter response with first-order derivatie of Gaussian filter (binary 
# image out+name.tiff).

# There are 4 parameters to be adjust, L: the length of the neighborhood along the y-axis, 
# sigma: the standard deviation of Gaussian function, w: the kernel size of the low-pass 
# filter before compute MFR-FDoG, c: threshold coefficient.

import numpy as np
import cv2
from math import exp, pi, sqrt