
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

def setlable(img, labimg, x, y, label):
    '''
    This fucntion is used for label image. 

    The first two input images are the image to be labeled and an output image with 
    labeled region. "x", "y" are the coordinate to be tested, "label" is the ID
    of a region.

    '''
    if img[y][x] and not labimg[y][x]:
        labimg[y][x] = label
        if inbounds(img.shape, (y, x+1)):
            setlable(img, labimg, x+1, y,label)
        if inbounds(img.shape, (y+1, x)):
            setlable(img, labimg, x, y+1,label)
        if inbounds(img.shape, (y, x-1)):
            setlable(img, labimg, x-1, y,label)
        if inbounds(img.shape, (y-1, x)):
            setlable(img, labimg, x, y-1,label)
        if inbounds(img.shape, (y+1, x+1)):
            setlable(img, labimg, x+1, y+1,label)
        if inbounds(img.shape, (y+1, x-1)):
            setlable(img, labimg, x-1, y+1,label)
        if inbounds(img.shape, (y-1, x+1)):
            setlable(img, labimg, x+1, y-1,label)
        if inbounds(img.shape, (y-1, x-1)):
            setlable(img, labimg, x-1, y-1,label)

def labelvessel(img, labimg, point, thresh, size, listcd): 
    '''
    This fucntion is used for generating a piece with paint-fill technique.  

    The first two input images are the image to be labeled and an output image with 
    labeled region. "point" is the coordinate to be tested, the "thresh" value the 
    threshld value of paint-fill, size is used to limit maximum size of a region and
    "listcd" is the list of coordinates of the pixels that are classified as vessel 
    in the piece. 

    '''
    if img[point[1]][point[0]] >= thresh and not labimg[point[1]][point[0]] and thresh:
        # print "img value: ", img[point[1]][point[0]], "thresh: ", thresh
        labimg[point[1]][point[0]] = 1
        x = point[0]
        y = point[1]
        listcd.append([x, y])
        size += 1
        try:
            if size > 500:
                return False
            if inbounds(img.shape, (y, x+1)):
                labelvessel(img, labimg, (x+1, y),thresh, size, listcd)
            if inbounds(img.shape, (y+1, x)):
                labelvessel(img, labimg, (x, y+1),thresh, size, listcd)
            if inbounds(img.shape, (y, x-1)):
                labelvessel(img, labimg, (x-1, y),thresh, size, listcd)
            if inbounds(img.shape, (y-1, x)):
                labelvessel(img, labimg, (x, y-1),thresh, size, listcd)
            if inbounds(img.shape, (y+1, x+1)):
                labelvessel(img, labimg, (x+1, y+1),thresh, size, listcd)
            if inbounds(img.shape, (y+1, x-1)):
                labelvessel(img, labimg, (x-1, y+1),thresh, size, listcd)
            if inbounds(img.shape, (y-1, x-1)):
                labelvessel(img, labimg, (x-1, y-1),thresh, size, listcd)
            if inbounds(img.shape, (y-1, x+1)):
                labelvessel(img, labimg, (x+1, y-1),thresh, size, listcd)
        except Exception, e:
            print "error: ", Exception, " in paint_fill..."

class Probe:
    '''
    The class Probe is to implement probes in the region of  interest. 

    To inicialize the probe, we need histogram threshold value, the minimum 
    and maximum size of the generated region, the maximum value of fringing 
    and maximum value of branch (Ttree).

    The init_queue function is to generate the inicial queue of probes with 
    given image. 

    The paint_fill function is to implement region growing with given threshld 
    value.

    The test function is to test the given region with 5 different tests.

    The label fucntion is to mark the given piece into vessel.

    The addpoints funciton is to add new probes to the end of queue.

    The deletepoint funciton is to delete the probes that locate the previous 
    veesel-classified pixel.

    '''
    def __init__(self, thresh, smin, smax, fringe, tree):
        self.th = thresh
        self.smin = smin
        self.smax = smax
        self.fg = fringe
        self.tree = tree

    def init_queue(self, mfr0):
        # generate the histogram of MFR 
        originalimg = cp.copy(mfr0)
        mfr = cp.copy(mfr0)
        h, w = mfr.shape
        hist,bins = np.histogram(mfr.ravel(),256,[0,256])
        for i in range(len(hist)):
            if hist[i] > self.th:
                hist[i] = 0
        h, w = mfr.shape
        for y in range(h):
            for x in range(w):
                if not hist[mfr[y][x]]:
                    mfr[y][x] = 0
                else:
                    mfr[y][x] = 1
        threshimg = cp.copy(mfr)

        # optimal option
        # ret,mfr = cv2.threshold(mfr, 10, 255, cv2.THRESH_BINARY)
        # thinning the threshold image
        thmfr = thinning(mfr)
        thinningimage = cp.copy(thmfr)

        # erase branchpoints
        for y in range(1,h-1,1):
            for x in range(1,w-1,1):
                if x == 0 or y == 0 or x == w-1 or y == h-1:
                    continue 
                p2 = int(thmfr[y-1, x])
                p3 = int(thmfr[y-1, x+1])
                p4 = int(thmfr[y, x+1])
                p5 = int(thmfr[y+1, x+1])
                p6 = int(thmfr[y+1, x])
                p7 = int(thmfr[y+1, x-1])
                p8 = int(thmfr[y, x-1])
                p9 = int(thmfr[y-1,x-1])
                num = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
                if num >= 3:
                    thmfr[y, x] = 0

        nonbranch = cp.copy(thmfr)

        # discard segments < 10 pixels
        lab = 1
        label = np.zeros(thmfr.shape)
        for y in range(h):
            for x in range(w):
                if not label[y][x] and thmfr[y][x]:
                    setlable(thmfr, label, x, y, lab)
                    lab += 1
        num = np.zeros(lab)
        for y in range(h):
            for x in range(w):
                num[label[y][x]-1] += 1
        for y in range(h):
            for x in range(w):
                if num[label[y][x]-1] <= 10:
                    thmfr[y][x] = 0
        remove = cp.copy(thmfr)
        
        # return initialized probe queue
        # find endpoints for queue
        queue = []

        for y in range(1,h-1,1):
            for x in range(1,w-1,1):
                if x == 0 or y == 0 or x == w-1 or y == h-1:
                    continue 
                p2 = int(thmfr[y-1, x])
                p3 = int(thmfr[y-1, x+1])
                p4 = int(thmfr[y, x+1])
                p5 = int(thmfr[y+1, x+1])
                p6 = int(thmfr[y+1, x])
                p7 = int(thmfr[y+1, x-1])
                p8 = int(thmfr[y, x-1])
                p9 = int(thmfr[y-1,x-1])
                num = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
                if num == 1:
                    queue.append([x, y])
        pointimg = cp.copy(thmfr)
        return queue

    def paint_fill(self, img, labelimg, p, T): 
        size = 0
        listcd = []
        labelvessel(img, labelimg, p, T, size, listcd)
        return (np.count_nonzero(labelimg), labelimg, listcd)

    def tests(self, size, piece, T, vessel, listcd):

        if size > 30:
            print "--test 0 pass--"
            # first, the size must less than smax
            if size > self.smax:
                print "--test 1 false--"
                return False

            # second, the threshold must be positive
            if T <= 1:
                print "--test 2 false--"
                return False

            # third, the piece cannot touch the vessel-classied pixel
            logpiece = piece > 0
            logvessel = vessel > 0
            result = logpiece & logvessel
            if result.sum() > 0:
                print "--test 3 false--"
                return False

            # fourth, border-pixels-touching-another-piece / total-pixel-in-piece
            h, w = piece.shape[:2]
            border = 0
            for x, y in listcd:
                if x == 0 or y == 0 or x == w-1 or y == h-1:
                    continue 
                p2 = int(piece[y-1, x])
                p3 = int(piece[y-1, x+1])
                p4 = int(piece[y, x+1])
                p5 = int(piece[y+1, x+1])
                p6 = int(piece[y+1, x])
                p7 = int(piece[y+1, x-1])
                p8 = int(piece[y, x-1])
                p9 = int(piece[y-1,x-1])
                num = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
                vp2 = int(vessel[y-1, x])
                vp3 = int(vessel[y-1, x+1])
                vp4 = int(vessel[y, x+1])
                vp5 = int(vessel[y+1, x+1])
                vp6 = int(vessel[y+1, x])
                vp7 = int(vessel[y+1, x-1])
                vp8 = int(vessel[y, x-1])
                vp9 = int(vessel[y-1,x-1])
                touch = vp2 + vp3 + vp4 + vp5 + vp6 + vp7 + vp8 + vp9 
                if num != 8 and touch:
                    border += 1
            if (border / logpiece.sum()) > self.fg:
                print "--test 4 false--"
                return False

            # fifth, total-pixel-in-piece / branches-in-piece
            listcd.sort()
            temppiece, indexskeleton = indirectindexing(listcd, piece)
            branch = 0
            for x, y in indexskeleton:
                if x == 0 or y == 0 or x == w-1 or y == h-1:
                    continue 
                p2 = int(temppiece[y-1, x])
                p3 = int(temppiece[y-1, x+1])
                p4 = int(temppiece[y, x+1])
                p5 = int(temppiece[y+1, x+1])
                p6 = int(temppiece[y+1, x])
                p7 = int(temppiece[y+1, x-1])
                p8 = int(temppiece[y, x-1])
                p9 = int(temppiece[y-1,x-1])
                num = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
                if num >= 3:
                    branch += 1 
            if (logpiece.sum() / branch) < self.tree:
                print "--test 5 false--"
                return False

            print "--tests pass!--"
            return True
        else:
            print "--test 0 false--"
            # second, the threshold must be positive
            if T <= 1:
                print "--test 2 false--"
                return False

            # third, the piece cannot touch the vessel-classied pixel
            logpiece = piece > 0
            logvessel = vessel > 0
            result = logpiece & logvessel
            if result.sum() > 0:
                print "--test 3 false--"
                return False

            return True

    def label(self, vessel, tempvessel):
        return (vessel | tempvessel)

    def addpoints(self, queue, vesselpiece, vessel, listcd):
        tempvessel, indexskeleton = indirectindexing(listcd, vesselpiece)
        h, w = piece.shape[:2]
        for x, y in indexskeleton:
            if x == 0 or y == 0 or x == w-1 or y == h-1:
                    continue 
            p2 = int(tempvessel[y-1, x])
            p3 = int(tempvessel[y-1, x+1])
            p4 = int(tempvessel[y, x+1])
            p5 = int(tempvessel[y+1, x+1])
            p6 = int(tempvessel[y+1, x])
            p7 = int(tempvessel[y+1, x-1])
            p8 = int(tempvessel[y, x-1])
            p9 = int(tempvessel[y-1,x-1])
            num = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
            if num == 1:
                point = [x, y]
                if not checkidentical(queue, point, vessel):
                    queue.append(point)
        return queue

    def deletepoint(self, queue, vessel, num):
        que = cp.copy(queue)
        count = 0
        for j in range(num, len(queue), 1):
            p = [0, 0]
            p[1], p[0] = queue[j][1], queue[j][0]
            num = vessel[p[1]][p[0]] + vessel[p[1]+1][p[0]] + vessel[p[1]][p[0]+1] +\
                  vessel[p[1]][p[0]-1] + vessel[p[1]-1][p[0]]     
            if num > 2:
                que.pop(j-count)
                count += 1
        return que

def checkidentical(l, point, vessel):
    '''
    This function is used for check if the given two points are same.

    '''
    for i in l:
        if i == point:
            return True
    return False

def indirectindexing(listcd, img):
    '''
    This function used indrect index approach to thin the given piece.

    '''
    prev = np.zeros_like(img)
    diff = np.ones_like(img)
    indexskeleton = []
    while cv2.countNonZero(diff) > 15:
        print "  find skeleton using indirect image indexing..."
        img, indexskeleton = indirectIteration(listcd, img, indexskeleton, 0)
        img, indexskeleton = indirectIteration(listcd, img, indexskeleton, 1)
        diff = cv2.absdiff(img, prev)
        prev = cp.copy(img)
    return img, indexskeleton

def indirectIteration(listcd, im, indexskeleton, iter):
    '''
    This function is the interation of indirectindexing.

    '''
    h, w = im.shape[:2]
    marker = np.ones(im.shape)
    for x, y in listcd:
        if x == 0 or y == 0 or x == w-1 or y == h-1:
            continue 
        p2 = int(im[y-1, x])
        p3 = int(im[y-1, x+1])
        p4 = int(im[y, x+1])
        p5 = int(im[y+1, x+1])
        p6 = int(im[y+1, x])
        p7 = int(im[y+1, x-1])
        p8 = int(im[y, x-1])
        p9 = int(im[y-1,x-1])

        A = (p2 == 0 and p3 == 1) + (p3 == 0 and p4 == 1) + \
            (p4 == 0 and p5 == 1) + (p5 == 0 and p6 == 1) + \
            (p6 == 0 and p7 == 1) + (p7 == 0 and p8 == 1) + \
            (p8 == 0 and p9 == 1) + (p9 == 0 and p2 == 1)
        B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
        if iter == 0:
            m1 = p2 * p4 * p6
            m2 = p4 * p6 * p8
        else:
            m1 = p2 * p4 * p8
            m2 = p2 * p6 * p8
        if A == 1 and (B >= 2 and B <= 6) and m1 == 0 and m2 == 0:
            marker[y,x] = 0
    for x, y in listcd: