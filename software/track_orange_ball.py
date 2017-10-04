

from collections import deque
import numpy as np
import argparse
import imutils
import cv2


ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
 	help="max buffer size")
args = vars(ap.parse_args())


orangeLower = (0, 87, 255)
orangeUpper = (255, 255, 255)
pts = deque(maxlen=args["buffer"])


camera = cv2.VideoCapture(1)
while True:
    # grab the current frame
    (grabbed, frame) = camera.read()



    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "orange", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, orangeLower, orangeUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        cv2.putText(frame, "dx: {}, dy: {}".format(x, y),
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (0, 0, 255), 1)

        # only proceed ifd the radius meets a minimum size
        if radius > 10:
            cv2.circle(frame, center, 5, (0, 0, 255), -1)


    # show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()