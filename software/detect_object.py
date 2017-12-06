

import cv2
import numpy as np
import imutils

## Ball has to be lower than 40px, or it is noise from outside.
## I do not want to ruin track(), therefore new  function.
ballmask = np.zeros((450, 600), dtype=np.uint8)
cv2.rectangle(ballmask, (0,40), (600, 450), (255), thickness = -1)
def find_ball(hsv, colorlower, colorupper):
    #i presume resized, HSV!!! frame here
    #if hsv.shape[:2] != ballmask.shape[:2]:
    #    raise "Resiizing error!"
    #ballframe = hsv.copy()
    ballframe = cv2.bitwise_and(hsv, hsv, mask = ballmask)
    return track(ballframe, colorlower, colorupper)

def percentage_of_color(hsv, lower, upper):
    mask = cv2.inRange(hsv, lower, upper)
    count = np.count_nonzero( mask )
    #print ("COUNTOFCOLOR:" + str(count) + " SHAPE: " + str(hsv.shape))
    #return float(count) / (hsv.shape[0] * hsv.shape[1])
    return count

def track(frame, colorlower, colorupper):
    # i put rezising (which we probably do not need) and converting to HSV to main loop

	# construct a mask for the color "orange", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(frame, colorlower, colorupper)
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=1)

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



        # only proceed ifd the radius meets a minimum size
        #if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            #cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
            #cv2.circle(frame, center, 5, (0, 0, 255), -1)
    else :
        x = -1
        y = -1
        radius = -1
        center = (-1, -1)
    return x, y, radius, center, mask


if __name__ == "__main__":
    import config
    camera = cv2.VideoCapture(0)

    while True:
        (grabbed, frame) = camera.read()
        frame = imutils.resize(frame, width=600)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        ball_x1, ball_y1, ball_radius1, ball_center1, ball_mask = find_ball(hsv, config.BALL_LOWER, config.BALL_UPPER)
        cv2.circle(frame, ball_center1, 10, (0, 0, 255), -1)

        cv2.imshow("ballmask", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
