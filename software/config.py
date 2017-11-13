# Proposed way of quickly choosing proper configuration, depending on computer where it runs.
# there are definitely many much better solutions. More complicated also.
# it seems that "from config import *" does exactly what I expect it to.
import platform

#must be manually set before match
FIELD_ID = 'A'
ROBOT_ID = 'Z'
BRAKES_ON = False #if BRAKES_ON then _no movement_ must occur.
				  #referee can turn it on and off

#need to be measured in real life
ARUCOWIDTH = 138 #real-life width of aruco marker, black border edge-to-edge
ARUCODISTANCE = 250 #distance between two markers, center-to-center
#basket is defined by two aruco markers and optionally blob of color (HSV) (not implemented).
#RAL code did not give meaningful detection, therefore manual calibration is required
BASKET = (10, 11,   (122, 77, 58), (157, 139, 201)) #Magenta RAL4010
#BASKET = (21, 22,   (101, 227, 157) ,(255, 255, 255)) #Blue RAL5015




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
