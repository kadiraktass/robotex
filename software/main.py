#!/usr/bin/python2.7
#
#   MAIN.PY IS AUTOMATICALLY STARTED ON REBOOT
#

import cv2
import detect_object
import movement
import communication

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
greenLower = (49, 180, 100)
greenUpper = (88, 255, 255)

camera = cv2.VideoCapture(0)


i=0

communication.send_soon("init") #does'nt do anything besides clearing buffers

try:
	while 1:

	    (grabbed, frame) = camera.read()

	    ball_x1, ball_y1, ball_radius1, ball_center1, ball_mask = detect_object.track(camera, greenLower, greenUpper)
	    basket_radius = -1
	    basket_x = -1

	    #if ball_radius1 > 10:
	    #    cv2.circle(frame, ball_center1, 5, (0, 0, 255), -1)

	    cv2.imshow("mask", ball_mask)

	    m1,m2,m3 = movement.get_command(ball_x1, ball_radius1, basket_x, basket_radius)
        print("sent by the main: ",m1,m2,m3)
		communication.set_motors(m1,m2,m3)

        #communication.set_thrower(0)
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
