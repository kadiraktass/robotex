#!/usr/bin/python2.7
#
#   MAIN.PY IS AUTOMATICALLY STARTED ON REBOOT
#

import cv2
import detect_object
import movement
import communication
import detect_aruco
import numpy as np
import imutils

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

#hsv values for the BALL!!
#greenLower = (40, 255, 45)
#greenUpper = (60, 255, 255)
greenLower = (32, 223, 33)
greenUpper = (55, 255, 192)

camera = cv2.VideoCapture(0)

camera.set(13, 0.40)
camera.set(14, 0.04)

communication.send_soon("init")

thrower_speed = 0

blinds = cv2.imread('horseblinds.png', 0)


try:
    while 1:

        (grabbed, frame) = camera.read()
        print("grabbed = ",grabbed)
        frame = cv2.bitwise_and(frame, frame, mask = blinds)
        # resize the frame, blur it, and convert it to the HSV
        frame = imutils.resize(frame, width=600)
        # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        ball_x1, ball_y1, ball_radius1, ball_center1, ball_mask = detect_object.track(frame, greenLower, greenUpper)
        cv2.circle(frame, ball_center1, 10, (0, 0, 255), -1)
        cv2.imshow("mask", ball_mask)

        basket_dist, basket_x, basket_corners, basket_ids = detect_aruco.detect_basket(frame)

        communication.update_comms()
        print("ball_y = ", ball_y1)
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
            communication.send_now("sm:0:0:0")
            communication.send_now("st:0")
            break
        elif key == ord('s'): # take a screenshot
            cv2.imwrite('screenshot.png', frame)

except KeyboardInterrupt:
    communication.send_now("sm:0:0:0")
    communication.send_now("st:0")

camera.release()
cv2.destroyAllWindows()
