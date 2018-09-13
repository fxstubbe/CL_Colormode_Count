# -*- coding: utf-8 -*-
"""
C.elegans counter

    Count number of worms on a given picture

    python worm_counter.py -i [imagefile] -o [imagefile]

@author: François-Xavier Stubbe
"""

#----------------------------------------------------------------------------------------------------------------------

import numpy as np
from statistics import median
import argparse
import imutils
import cv2
import warnings
import sys
import os.path

#-----------------------------------------------------------------------------------------------------------------------
"""
Construct the argument parse and parse the arguments
"""
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--image", required=True,
    help="path to the input image")
parser.add_argument("-o", "--output", required=False,
    help="path to the output image")
parser.add_argument("-c", "--colormode", required = False,
    help="Choose the color mode, default is GFP" )
parser.add_argument("-v", "--RGBvector", required = False,
    help="path to a file containing upper and lower RGB vector (number,number,number)" )
args = vars(parser.parse_args())

#If input file does not exist, exit
if os.path.exists(args["image"]) is False:
	print('Path to input file is not valid')
	sys.exit(0)


#----------------------------------------------------------------------------------------------------------------------
"""
Loading Image
"""

# load the image
image_orig = cv2.imread(args["image"])
height_orig, width_orig = image_orig.shape[:2]

# output image with contours
image_contours = image_orig.copy()
#----------------------------------------------------------------------------------------------------------------------
"""
Detecting worms ; The detection is performed by color (given as a GBR vector)
"""
#Initialize the counter
counter = 0

# copy of original image
image_to_process = image_orig.copy()

#---------------------------------------------------------------------------------------------------------------------
"""
Initialize the color mode, default is GFP
"""

colormode = args["colormode"]
RGBvector = args["RGBvector"]

if colormode is None:
    color ='GFP'
if colormode == 'GFP':
	color = 'GFP'
if colormode == 'mCherry':
	color = 'mCherry'
if RGBvector is not None:
	print('Running with custom RGB vectors')
	color = 'Custom'
#else:
    #color = colormode

if color is None:
	print('Error, no color mode selected')
	sys.exit(0)

# define NumPy arrays of color boundaries (GBR vectors)
if color == 'GFP':
    lower = np.array([ 0, 51,  0])
    upper = np.array([181, 252, 184])
    print('Running in GFP color mode')
if color == 'mCherry':
    lower = np.array([ 0, 0,  68])
    upper = np.array([4, 1, 220])
    print('Running in mCherry color mode')
if color == 'Custom':
    with open(RGBvector) as vectorfile:
        data=[[float(x) for x in line.strip().split(',')] for line in  vectorfile]
        lower = np.array(data[0])
        upper = np.array(data[1])

if color not in ['GFP', 'mCherry', 'Custom'] :
    print(str(color) + ' is not a defined colormode. Available colormode are GFP, mCherry and Custom')
    sys.exit(0)

# find the colors within the specified boundaries
image_mask = cv2.inRange(image_to_process, lower, upper)
# apply the mask
image_res = cv2.bitwise_and(image_to_process, image_to_process, mask = image_mask)

## load the image, convert it to grayscale, and blur it slightly
image_gray = cv2.cvtColor(image_res, cv2.COLOR_BGR2GRAY)
image_gray = cv2.GaussianBlur(image_gray, (5, 5), 0)

# perform edge detection, then perform a dilation + erosion to close gaps in between object edges
image_edged = cv2.Canny(image_gray, 50, 100)
image_edged = cv2.dilate(image_edged, None, iterations=1)
image_edged = cv2.erode(image_edged, None, iterations=1)

# find contours in the edge map
cnts = cv2.findContours(image_edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if imutils.is_cv2() else cnts[1]

#-----------------------------------------------------------------------------------------------------------------------
"""
We cannot distinguish touching worms. Based on the median worm' surface, we divide "big" worms into smaller ones
to get a more accurate count
"""

with warnings.catch_warnings(): #Here we expect to see a RuntimeWarning
    warnings.simplefilter("ignore", category=RuntimeWarning) #We do not want to output the warning
    array = np.array([cv2.contourArea(worm) for worm in cnts if cv2.contourArea(worm) < 300 ])
    if array.size == 0: #There is a statistical error if the array is empty
        array = np.zeros(1) #Ff the array is empty, we make an array containing a 0
    else : #We make an array containing the values in range of 25% around the median
        med = median(array)
        array = array[(array < ((med + (0.25*med))))]
        array = array[(array > ((med - (0.25*med))))]

#------------------------------------------------------------------------------------------------------------------------
"""
We loop over each contours, if it's too big we divide it by the mean of the array previously made (centered around the median)
We write on the output file in how many worms it has been divided
"""
# loop over the contours individually
for c in cnts:
    #print(cv2.contourArea(c))
    #if the contour is not sufficiently large, ignore it
    if cv2.contourArea(c) > 1.5*np.mean(array) :
        mean = round(cv2.contourArea(c)/np.mean(array))
        counter += mean
        hull = cv2.convexHull(c)
        cv2.drawContours(image_contours,[hull],0,(255,0,0),1)
        cv2.putText(image_contours, "{:.0f}".format(round(cv2.contourArea(c))/np.mean(array)), (int(hull[0][0][0]), int(hull[0][0][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        continue

    # compute the Convex Hull of the contour
    hull = cv2.convexHull(c)

    # prints contours in red color
    cv2.drawContours(image_contours,[hull],0,(0,0,255),1)

    counter += 1

# Print the number of womrs
counter = int(counter)
print("#worms : ",counter, "\n")
cv2.putText(image_contours, "#Worms : " + str(counter), (5,315), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

# Writes the output image if a path is specified
if args["output"] is None:
	sys.exit(0)
else:
	cv2.imwrite(args["output"],image_contours)
