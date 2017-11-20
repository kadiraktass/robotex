

import cv2
import numpy as np
import imutils

#hsv values for the object1
orangeLower = (0, 192, 142)
orangeUpper = (255, 255, 255)

def track(frame, colorlower, colorupper):

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
	
    # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	
	# construct a mask for the color "orange", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, colorlower, colorupper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
	
	# find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
    im2, contours, hierarchy = cv2.findContours(mask.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)                       
    center = None
    
	# only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        contour_area = cv2.contourArea(c)
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
    return x, y, radius, center, mask,contour_area

camera = cv2.VideoCapture(0)

camera.set(13, 0.40)
camera.set(14, 0.04)

while 1:    
    
    (grabbed, frame) = camera.read()
    x,y,radius,center,mask,contour_area = track(frame, orangeLower, orangeUpper)
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)
    print(contour_area)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break    
    
camera.release()
cv2.destroyAllWindows()
   