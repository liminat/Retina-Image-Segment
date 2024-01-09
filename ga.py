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

# in order to reduce the quantization error, we convert the 
# 8-bit image to float image. 
im1 = im1.astype(np.float32) / 255.0
gt = gt.astype(np.float32) / 255.0

# create two variables of individual and fitness function. 
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

# create a base variable in DEAP
toolbox = base.Toolbox()

# func is used for randomly generate individual with different range 
# of parameters: 
# L: the length of the neighborhood along the y-axis to smooth noise (1-15)
# sigma: the standard deviation of Gaussian function
# w: the kernel size of the low-pass filter before compute MFR-FDoG
# c: the gain of threshold
func = [lambda:random.randint(1, 15), lambda:random.uniform(0.35, 10), \
        lambda:random.randint(3, 50), lambda:random.uniform(0.1, 5)]

# Structure initializers
# define 'individual' to be an individual
# consisting of 4 parameters generated by func.
toolbox.register("individual", tools.initCycle, creator.Individual, 
    func, 1)

# define the population to be a list of individuals
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# define the number of individual 
numi = 0

# the goal ('fitness') function to be maximized
# the fitness function is Dice coefficient. 
def evalOneMax(individual):
    global numi
    # compute runing time of each individual
    evalstart = timeit.default_timer()

    # define a varialbe of matched filter response.
    matched = mfr.MFR(individual[0], individual[1], individual[2], individual[3])

    # generate Gaussian and first-order derivative of Gaussian filers and their 
    # filter bank.
    gf = matched.gaussian_matched_filter_kernel()
    fdog = matched.fdog_filter_kernel()
    bank_gf = matched.createMatchedFilterBank(gf, 12)
    bank_fdog = matched.createMatchedFilterBank(fdog, 12)

    # generate matched filter response of both filters.
    H = matched.applyFilters(im1, bank_gf)
    D = matched.applyFilters(im1, bank_fdog)

    # compute the threshold value using MFR-FDoG
    kernel = np.ones((matched.w,matched.w),np.float32)/(matched.w*matched.w)
    dm = np.zeros(D.shape,np.float32)
    DD = np.array(D, dtype='f')
    dm = cv2.filter2D(DD,-1,kernel)
    dmn = cv2.normalize(dm, dm, 0, 1, cv2.NORM_MINMAX)
    uH = cv2.mean(H)
    Tc = matched.c * uH[0]
    T = (1+dmn) * Tc 

    # compute Dice coefficient.
    a, b, i = 0., 0., 0.
    (h, w) = H.shape
    for y in range(h):
        for x in range(w):
            if H[y][x] >= T[y][x] and gt[y][x]:
                i += 1
                a += 1
                b += 1
            elif H[y][x] >= T[y][x] and not gt[y][x]:
                a += 1
            elif H[y][x] < T[y][x] and gt[y][x]:
                b += 1
            elif H[y][x] < T[y][x] and not gt[y][x]:
                pass
    dice = 2*i/(a+b)

    # compute runing time of each individual
    evalstop = timeit.default_timer()
    numi += 1
    print "individual: ", numi, ": ", individual, "  dice: ", round(dice, 2), \
          "time consuming: ", round(evalstop - evalstart, 2)
    return dice,

#----------
# Operator registration
#----------
# register the goal / fitness function
toolbox.register("evaluate", ev