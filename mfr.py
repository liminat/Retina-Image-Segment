

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
from numbapro import vectorize
import sys

class MFR:
    '''
    MFR class requests L, sigme, w, c to inicialize. 

    This class is used for generate filter of Gaussian (gaussian_matched_filter_kernel) and 
    first-order derivative of Gaussian (fdog_filter_kernel)and the filter bank of the previous 
    filters (createMatchedFilterBank). applyFilters function used for generate the matched filter
    response of the given filter. 

    '''

    def __init__(self, L, sigma, w, c):
        if L == 0:
            L = 1
        if sigma == 0:
            sigma = 1
        if w == 0:
            w = 1
        self.L = L
        self.sigma = sigma
        self.w = w
        self.c = c

    def _filter_kernel_mf_fdog(self, t = 3, mf = True):
        dim_y = int(self.L)
        dim_x = int(2 * t * self.sigma)
        if dim_x == 0:
            dim_x = 1
        if dim_y == 0:
            dim_y = 1
        arr = np.zeros((dim_y, dim_x), 'f')
        
        ctr_x = dim_x / 2 
        ctr_y = int(dim_y / 2.)

        # an un-natural way to set elements of the array
        # to their x coordinate. 
        # x's are actually columns, so the first dimension of the iterator is used
        it = np.nditer(arr, flags=['multi_index'])
        while not it.finished:
            arr[it.multi_index] = it.multi_index[1] - ctr_x
            it.iternext()

        two_sigma_sq = 2 * self.sigma * self.sigma
        if two_sigma_sq == 0:
            two_sigma_sq = 1
        div = sqrt(2 * pi) * self.sigma
        if div == 0:
            div = 1.
        sqrt_w_pi_sigma = 1. / div
        if not mf:
            div = self.sigma ** 2
            if div == 0: