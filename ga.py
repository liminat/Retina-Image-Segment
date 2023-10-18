# This file uses genetic algorithm to optimaize the parameters of 
# matched filter response.

# In this script, we use DEAP to implement genetic algorithm. You 
# can install it follow the link: https://github.com/DEAP/deap.

# The input files are original image and its ground truth image and 
# the output is the optimaized parameters.

import random
import mfr
from deap import base
from d