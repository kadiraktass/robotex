#!/usr/bin/python2.7
#
#   MAIN.PY IS AUTOMATICALLY STARTED ON REBOOT
#

import cv2
import detect_object
import movement
import communication
import detect_aruco

#hsv values for the object1
orangeLower = (0, 136, 232)
orangeUpper = (255, 255, 255)

#hsv values for the object2
blueLower = (88, 160, 133)
blueUpper = (255, 255, 255)

#hsv values for the object3
whiteLower = (0, 0, 255)
whiteUpper = (0, 0, 255)

#hsv values for the object4
redLower = (0, 86, 182)
redUpper = (10, 255, 255)

#hsv values for the object5
#greenLower = (40, 255, 45)
#greenUpper = (60, 255, 255)
greenLower = (41, 220, 83)
greenUpper = (62, 255, 255)

camera = cv2.VideoCapture(0)

camera.set(13, 0.40)
camera.set(14, 0.04)

i=0

communication.send_soon("init") #does'nt do anything besides clearing buffers
thrower_speed = 0
try:
	while 1:

	    (grabbed, frame) = camera.read()
	    print("grabbed = ",grabbed)
	    ball_x1, ball_y1, ball_radius1, ball_center1, ball_mask = detect_object.track(frame, greenLower, greenUpper)
	    basket_dist, basket_x, basket_corners, basket_ids = detect_aruco.detect_basket(frame)

	    #if ball_radius1 > 10:
	    #    cv2.circle(frame, ball_center1, 5, (0, 0, 255), -1)

	    cv2.imshow("mask", ball_mask)
	    communication.update_comms()
            print(ball_y1)
            m1,m2,m3,thrower_speed = movement.get_command(ball_x1, ball_radius1, basket_x, basket_dist)
            print("sent by the main: ",m1,m2,m3)
            communication.set_motors(m1,m2,m3)
	    
	    communication.update_comms()
            communication.set_thrower(thrower_speed)
	    cv2.putText(frame, "dx: {}, dy: {}, radius: {}".format(int(ball_x1), int(ball_y1), int(ball_radius1)),
	                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
	                    0.35, (0, 0, 255), 1)

            communication.update_comms()
            cv2.imshow("Frame", frame)

	    key = cv2.waitKey(1) & 0xFF
	    if key == ord("q"):
	        break

except KeyboardInterrupt:
	communication.set_motors(0,0,0)
	communication.set_thrower(0)

camera.release()
cv2.destroyAllWindows()
