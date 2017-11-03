# Proposed way of quickly choosing proper configuration, depending on computer where it runs.
# there are definitely many much better solutions. More complicated also.
# it seems that "from config import *" does exactly what I expect it to.
import platform

#must be set before match
FIELD_ID = 'A'
ROBOT_ID = 'Z'
BRAKES_ON = False #if BRAKES_ON then no movement must occur. communication.set_motors doesnt pass it to the MB.




# computer-specific stuff
if platform.node() == 'riiul-nuc': #our robot
	serialport = "/dev/ttyACM0"
	cameranum = 0

elif platform.node() == 'platypus': #Hannes' 'puter
	serialport = "/dev/ttyACM1"
	cameranum = 0

else: #most likely Kadir
	print( "computer: " + platform.node() )
	serialport = "COM3"
	cameranum = 1
