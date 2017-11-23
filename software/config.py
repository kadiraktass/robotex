# Proposed way of quickly choosing proper configuration, depending on computer where it runs.
# there are definitely many much better solutions. More complicated also.
# it seems that "from config import *" does exactly what I expect it to.
import platform
import pickle

#must be manually set before match
FIELD_ID = 'A'
ROBOT_ID = 'A'
#choose one:
#TARGET_BASKET = 'blue'
TARGET_BASKET = 'magenta'

BRAKES_ON = True #if BRAKES_ON then _no movement_ must occur.
				  #referee can turn it on and off


#need to be measured in real life
#ARUCOWIDTH = 138 #real-life width of aruco marker, black border edge-to-edge
#ARUCODISTANCE = 250 #distance between two markers, center-to-center
#basket is defined by two aruco markers and optionally blob of color (HSV) (not implemented).
#RAL code did not give meaningful detection, therefore manual calibration is required


#BASKET = (10, 11,   (0, 0, 0), (12, 244, 114)) #Magenta RAL4010
#BASKET = (21, 22,   (63, 150, 0),  (128, 255, 150)) #Blue RAL5015


##############################################################################
#read color limits from file
colorvals = pickle.load( open( "color_values.pkl", "rb" ) )
print ("From color config file read: " + str(colorvals))

if TARGET_BASKET == 'magenta':
    BASKET = [10, 11, (), ()]
    BASKET[2] = colorvals['basket_magenta'][0]
    BASKET[3] = colorvals['basket_magenta'][1]

elif TARGET_BASKET == 'blue':
    BASKET = [21, 22, (), ()]
    BASKET[2] = colorvals['basket_blue'][0]
    BASKET[3] = colorvals['basket_blue'][1]

BALL_LOWER = colorvals['ball'][0]
BALL_UPPER = colorvals['ball'][1]

CARPET_LOWER = colorvals['carpet'][0]
CARPET_UPPER = colorvals['carpet'][1]




# computer-specific stuff
if platform.node() == 'riiul-nuc': #our robot
	serialport = "/dev/ttyACM0"
	cameranum = 0

elif platform.node() == 'platypus': #Hannes' 'puter
	serialport = "/dev/ttyACM0"
	cameranum = 0

else: #most likely Kadir
	print( "computer: " + platform.node() )
	serialport = "COM3"
	cameranum = 1
