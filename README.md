# CL_Colormode_Count
This computer vision project aims to the creation of program capable to count the number of C. elegans on a petridish. It has to work in different colormode (GFP, mCherry, Custom)


Argument : 

-i path to the input image (Required)
-o path to the output image (Not Required)
-c colormode (can either be : GFP, mCherry or Custom; Default is GFP ; Not Required)
-v path to text file containing upper and lower RGB on different line (works with Custom Colormode or override other colormodes ; Not required)


Worms are detected by their color (color recognition in between boundaries, given as RGB vetors) and edge detection is then performed. Once worms have been detected on the picture, their area is calculated. If worms are touching, they are only detected as one worm. To counter that, we calculate the median of those area (if they are not too big, we aim to calculate the median of individual womrs). We then calculate the average area for worms around the median (25% up and down). This is used to divide the "big worms" (potentially multiple worms). 

Single worms are circled in red. "Big worms" (potentially multiple worms) are circled in blue and the number of worms count is written on the image. 

The final worm count is displayed on the image as well as in the console. 

