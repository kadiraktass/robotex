#!/usr/bin/python2.7 
#
#   MAIN.PY IS AUTOMATICALLY STARTED ON REBOOT
#
#   Problem - on different platforms there are serial ports and probably some other things differently defined, or in different locations.
#   I dont know a perfect solution, am only proposing to detect computer name, and define config variables accordingly?
#   eg:

#import platform
#if platform.node() == 'riiul-nuc':
#	serialport = "/dev/ttyACM0" 
#	cameranum = 0
#else:
#	serialport = "COM3"
#	cameranum = 1
	
#gets messy. Stack it away somewhere.
from config import *


import cv2
import numpy as np
import detect_object
import movement
import serial

#hsv values for the object1
orangeLower = (0, 136, 232)
orangeUpper = (255, 255, 255)

#hsv values for the object2
blueLower = (89, 224, 84)
blueUpper = (255, 255, 255)

#hsv values for the object3
whiteLower = (0, 0, 255)
whiteUpper = (0, 0, 255)

#hsv values for the object4
redLower = (79, 210, 72)
redUpper = (255, 255, 255)

fow = 75

baud = 9600 
ser = serial.Serial(serialport, baud, timeout=1)


while 1:

    (grabbed, frame) = camera.read()
    
    x1, y1, radius1, center1, mask = detect_object.track(camera, whiteLower, whiteUpper)
    
    cv2.putText(frame, "dx: {}, dy: {}".format(x1, y1),
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (0, 0, 255), 1)
    if radius1 > 10:
        cv2.circle(frame, center1, 5, (0, 0, 255), -1)
    cv2.imshow("Frame", frame)
    cv2.imshow("mask", mask)
    cmd = movement.get_command(x1, y1, radius1, fow)
    
    ser.write(cmd + '\r\n')
    
    # if the 'q' key is pressed, stop the loop
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
