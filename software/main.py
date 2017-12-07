#!/usr/bin/python2.7
#
#   MAIN.PY IS AUTOMATICALLY STARTED ON REBOOT
#

import cv2
import detect_object
import movement
import communication
import detect_aruco2
import numpy as np
import imutils
import time
#from config import *
import config
import argparse

#COLOR VALUES ARE MOVED TO CONFIG.PY, or more precisely into color_values.pkl,
#which is written by hsv_range_detector.py

camera = cv2.VideoCapture(0)
#camera.set(13, 0.40) #hue
#camera.set(14, 0.04) #exposure

communication.send_soon("init")


thrower_speed = 0
last_throw = time.time()

blinds = cv2.imread('horseblinds.png', 0)


'''Command line:
    Command line parameters are not saved anywhere, so use always when needed.
    Defaults are AA, off, blue.
'''
parser=argparse.ArgumentParser()
parser.add_argument('--id', help='Field and robot: AA, AB, AC, BA...')
parser.add_argument('--brakes', help='Emergency brake is on or not: on/off')
parser.add_argument('--target', help='Where to throw: magenta or blue')
parser.add_argument('--tambov', help='linear adjustment of throwing distance')
args=parser.parse_args()

if not args.id is None:
    config.FIELD_ID = args.id[0]
    config.ROBOT_ID = args.id[1]
if not args.brakes is None:
    config.BRAKES_ON = True if args.brakes=='on' else False
if not args.target is None:
    config.TARGET_BASKET=args.target
    config.BASKET = config.MAGENTA_BASKET if args.target == 'magenta' else config.BLUE_BASKET

if not args.tambov is None:
    detect_aruco2.TAMBOV = int(args.tambov)
print (detect_aruco2.TAMBOV)

#print('PARAMS: FIELD=', FIELD_ID, ', ROBOT=', ROBOT_ID, ', BRAKES=', BRAKES_ON, ', TARGET=', TARGET_BASKET)
#input()

framestart = 0
try:
    while 1:

        (grabbed, frame) = camera.read()
        #print("grabbed = ",grabbed)
        frame = cv2.bitwise_and(frame, frame, mask = blinds)
        # resize the frame, blur it, and convert it to the HSV
        #frame = imutils.resize(frame, width=600)
        # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        ball_x1, ball_y1, ball_radius1, ball_center1, ball_mask = detect_object.find_ball(hsv, config.BALL_LOWER, config.BALL_UPPER)
        if ball_x1 >= 0:
            cv2.circle(frame, ball_center1, 10, (0, 0, 255), -1)
        cv2.imshow("mask", ball_mask)

        basket_dist, basket_x, basket_corners, basket_ids = detect_aruco2.detect_basket(frame)
        basket_dist = detect_aruco2.gimme_running_average(basket_dist)

        amount_of_carpet = detect_object.percentage_of_color(hsv, config.CARPET_LOWER, config.CARPET_UPPER)


        communication.update_comms()
        print("ball_y = ", ball_y1)
        m1,m2,m3,thrower_speed = movement.get_command(ball_x1, ball_y1,ball_radius1, basket_x, basket_dist, amount_of_carpet)
        print("sent by the main: ",m1,m2,m3)

        communication.set_motors(m1,m2,m3)
        now = time.time()
        communication.update_comms()
        if thrower_speed > 0:
            communication.set_thrower(thrower_speed)
            last_throw = now
        elif (now - last_throw) >= 3:
            communication.set_thrower(0)
        communication.update_comms()



        cv2.putText(frame, "CARPET: {}".format(int(amount_of_carpet)),
                            (50, 80), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 0, 255), 1)

        fps = round(1.0 / (time.time() - framestart))
        cv2.putText(frame, "FPS: {}".format( fps ),
                            (50, 100), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 0, 255), 1)

        cv2.putText(frame, "dx: {}, dy: {}, radius: {}".format(int(ball_x1), int(ball_y1), int(ball_radius1)),
                        (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        0.35, (0, 0, 255), 1)

        cv2.putText(frame, str( movement.activeState ),
                        (10, 420), cv2.FONT_HERSHEY_SIMPLEX,
                        0.45, (0, 0, 255), 1)

        cv2.line(frame, (320,100), (320,200), (0,0,255),1)

        cv2.imshow("Frame", frame)
        framestart = time.time()


        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            communication.send_now("sm:0:0:0")
            communication.send_now("st:0")
            break
        elif key == ord('b'):
            config.BRAKES_ON = False
            print ("BRAKES OFF")
        elif key == ord('s'): # take a screenshot
            cv2.imwrite('screenshot.png', frame)

except KeyboardInterrupt:
    communication.send_now("sm:0:0:0")
    communication.send_now("st:0")

camera.release()
cv2.destroyAllWindows()
