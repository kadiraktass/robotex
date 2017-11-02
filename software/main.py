
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

import cv2
import numpy as np
import detect_object
import movement
import serial
import time 

#hsv values for the object1
orangeLower = (0, 136, 232)
orangeUpper = (255, 255, 255)

#hsv values for the object2
blueLower = (62, 160, 133)
blueUpper = (255, 255, 255)

#hsv values for the object3
whiteLower = (0, 0, 255)
whiteUpper = (0, 0, 255)

#hsv values for the object4
redLower = (0, 86, 182)
redUpper = (10, 255, 255)

fow = 75

camera = cv2.VideoCapture(0)
port = "/dev/ttyACM0" 

baud = 9600 
ser = serial.Serial(port, baud, timeout=1)

lastcommand = ""
i=0

#ser.write("fs0" + '\r\n')

while 1:

    (grabbed, frame) = camera.read()
    
    x1, y1, radius1, center1, mask = detect_object.track(camera, blueLower, blueUpper)
    
    cv2.putText(frame, "dx: {}, dy: {}".format(x1, y1),
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (0, 0, 255), 1)
    if radius1 > 10:
        cv2.circle(frame, center1, 5, (0, 0, 255), -1)
    cv2.imshow("Frame", frame)
    cv2.imshow("mask", mask)
    cmd = movement.get_command(x1, y1, radius1, fow)
    
    if (cmd <> lastcommand):
        ser.write(cmd + '\r\n')
        lastcommand = cmd
 	print(cmd)
        print(lastcommand)
    else:
  	i=i+1
	print(i)
    if i==120:
        ser.write(cmd + '\r\n')
	print(cmd)
        i=0

    #ser.write(cmd + '\r\n' )
    #print(cmd)
    #print( ser.readline() )
    #time.sleep(0.5)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
