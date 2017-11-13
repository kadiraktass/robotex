#!/usr/bin/python2.7
#
#   MAIN.PY IS AUTOMATICALLY STARTED ON REBOOT
#

import cv2
import detect_object
import movement
import communication
import detect_aruco
import time

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
greenLower = (39, 191, 53)
greenUpper = (56, 255, 255)

camera = cv2.VideoCapture(0)

camera.set(13, 0.4)
camera.set(14, 0.04)

i=0

communication.send_soon("init") #does'nt do anything besides clearing buffers
throw_timeout = communication.millis()

try:
	while 1:

		(grabbed, frame) = camera.read()

		ball_x1, ball_y1, ball_radius1, ball_center1, ball_mask = detect_object.track(frame, greenLower, greenUpper)


		basket_dist, basket_x, basket_corners, basket_ids = detect_aruco.detect_basket(frame)

		m1,m2,m3,thrower_speed = movement.get_command(ball_x1, ball_radius1, basket_x, basket_dist)
		print("sent by the main: ",m1,m2,m3)

		communication.set_motors(m1,m2,m3)
		communication.update_comms()

		print("THROWER SPEED IN MAIN: ", thrower_speed)
		if thrower_speed > 0:
			communication.set_thrower( thrower_speed )
			throw_timeout = communication.millis()

		#reset to zero after some time
		if communication.millis() - throw_timeout > 7000:
			communication.set_thrower( 0 )
			throw_timeout = communication.millis()

		communication.update_comms()

		#lets put as much debugging information onto frame as possible
		cv2.putText(frame, "dx: {}, dy: {}, radius: {}".format(int(ball_x1), int(ball_y1), int(ball_radius1)),
	                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
	                    0.35, (0, 0, 255), 1)
		cv2.circle(frame, ball_center1, 5, (0, 0, 255), -1)
		cv2.imshow("mask", ball_mask)

		cv2.imshow("Frame", frame)

		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			break

except KeyboardInterrupt:
	communication.send_now('sm:0:0:0')
	communication.send_now('st:0')


camera.release()
cv2.destroyAllWindows()
