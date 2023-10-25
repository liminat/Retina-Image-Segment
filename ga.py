# This file uses genetic algorithm to optimaize the parameters of 
# matched filter response.

# In this script, we use DEAP to implement genetic algorithm. You 
# can install it follow the link: https://github.com/DEAP/deap.

# The input files are original image and its ground truth image and 
# the output is the optimaized parameters.

import random
import mfr
from deap import base
from deap import creator
from deap import tools
import numpy as np
import sys
import timeit
import cv2

# im0 is the original image and gt is its ground truth. 
# and then, we convert these images into grayscale images.
im0 = cv2.imread(sys.argv[1])
gt = cv2.imread(sys.argv[2])
im1 = cv2.cvtColor(im0, cv2.COLOR_BGR2GRAY)
gt = cv2.cvtColor(gt, cv2.COLOR_BGR2GRAY)

# in order to reduce the quantization error, 