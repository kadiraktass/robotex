'''
TODO: keep state 3 for 4 seconds or so and do not look for balls at that time.


Plan:
Distance is expressed in pixels
Converting to centimeters/etc will introduce additional errors.
Proper pose estimation requires calibrating camera and some arcane math.
I try first simpler variant.
Location of basket is given in pixels also (on horizontal axis only)


Process of calibration:
Put robot to a centerline, this is 250cm, measured from first edge of robot to backplate of basket.
Read distance in pixels, find neccessary speed for thrower, repeat and rinse, derive a function for a curve.
Introduce a quick calibration constant in case field of competition is slightly different.

Fuck it. I cannot detect both markers at the same time - i need to derive
all the nessecary information from just one of them.
Double fuck it. I cannot even detect a single marker under ideal conditions.
I need a fallback plan (blob detection)
'''


#
# In theory, AruCo markers can give us much more reliable information about basket distance (and heading),
# than measuring blobs.
#
# Tutorial (cpp): https://docs.opencv.org/3.1.0/d5/dae/tutorial_aruco_detection.html
# Tutorial (python): http://www.philipzucker.com/aruco-in-opencv/
# Generator: http://terpconnect.umd.edu/~jwelsh12/enes100/marker.html?id=22&size_mm=250&padding_mm=10
# magenta (color RAL4010) basket has markers with id of 10 and 11,
# blue (color RAL5015) basket has markers 20 and 21.
# Rules do not specify their distance from eachother, so we'd have third reliable measuring point.

# converting color: http://rgb.to/ral/4010




# opencv-contrib seems to be only release of opencv with aruco support built in.
# I saw some variants of selfcompiling the source and wrappers, but who wants to do that?

#fuuuuu.... k. Official pip package does not have ffmpg support, eg. no video for you. Me.
# No other choice left, but to recompile.
# https://www.pyimagesearch.com/2016/10/24/ubuntu-16-04-how-to-install-opencv/
# I'll do it for python 2.7 (and 3.4(!) - guide uses 3.5)
# NB! in step #2 downloaded version /3.3.0.zip
# I skipped over setting up virtual environments (because it failed)
# cmake: crazy errors were caused by typo in path to modules

#TODO: public function that takes frame, returns something about markers.
#possibly heading (x-coordinate) and id of basket, nuthing more.
#for debugging optionally modify, or return modified frame.

from __future__ import print_function
import cv2  #Seems there are big compatibility issues between versions. So we need to be on same lib.
import cv2.aruco as aruco
import numpy as np
from config import BASKET
import time

#help( cv2.aruco )
#possible interests:
#calibrateCameraAruco()




#ubuntu has problems with videocapture. Something about ffmpeg support.
#cap = cv2.VideoCapture(0)
#cap = skvideo.io.VideoCapture( 0 )
#timeout error: https://stackoverflow.com/questions/12715209/select-timeout-error-in-ubuntu-opencv

#cap.get and gap.set() for resolution

#aruco_dict = aruco.CustomDictionary_generate(25, 5) #original does work.
aruco_dict = aruco.Dictionary_get( aruco.DICT_ARUCO_ORIGINAL )
parameters =  aruco.DetectorParameters_create()

#"Corrupt JPEG data: premature end of data segment" with accompanied freezing is killing me. I need to recompile again??
#TODO: would it be reasonable to hold running average?
#and truthness level? (eg two arucos is best, blob worst)

#You cannot rely on finding basket from every frame. Therefore strategy is as follows:
#find basket, select speed, attack, hope for the best.

#TODO: maybe.
#if last dist was None more than 1s ago then we do not see basket.
#if we just saw it, but right now did'nt detect, then skip
#if we just saw it, and keep seeing, then keep running average to smooth out fluctuations

def calculate_thrower_speed( dist ):
    tambov = -20 #coefficent of precision. Yeah, just made up.
    #todo: actually,
    tambov2 = 0
    if dist > 0:
        #ehh, trying to add a little power to close and far throws
        #Lookup table is starting to make sense suddenly
        if dist > 160:
            tambov2 = dist - 160
        if dist < 40:
            tambov2 = (40 - dist)*5

        return int( 3381.8 * dist ** -0.5328 + tambov + tambov2)
    else:
        return 0



def detect_basket( frame ):
    #lists of ids and the corners belonging to each id

    corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
    #found something. Gives None or some numpy array.
    if ids is None:
        return fallback_to_blob(frame)

#    if isinstance(ids, np.ndarray): #for some sick reason, corners is a list of numpy arrays several levels deep
#        ids = ids.tolist()

    print ('IDS:' + str(ids))
#    print ('CORNERS:' + str(corners))

    #when i find rightmost marker, it means basket is a little bit leftwards.
    #ditto for left one. And arithmetic mean if both are visible.
    #oh hell, detection is horrible. Works only under ideal conditions.
    found = []
    dists = []
    basks = []
    #marker is (vertical_distance, x_of_basket)
    for i in range(0, len(ids)):
            topleft = corners[i][0][0]
            topright = corners[i][0][1]
            bottomleft = corners[i][0][3]
            height = bottomleft[1] - topleft[1]
            print (topleft, topright, bottomleft, height)

            if ids[i][0] == BASKET[0]: #left marker
                dists.append ( height )
                basks.append ( topright[0] + height/3 )

            if ids[i][0] ==  BASKET[1]: #right marker
                dists.append ( height )
                basks.append ( topleft[0] - height/3 )

#    print ('got:', end='')
#    print(dists, basks)

    #if i got both, return arithmetic mean
    if len(dists) == 0:
        return -1, -1, corners, ids

    return np.mean(dists), np.mean(basks), corners, ids

    #gray = aruco.drawDetectedMarkers(gray, corners)






def fallback_to_blob( frame ):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, BASKET[2], BASKET[3])
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        c = max(cnts, key=cv2.contourArea)
        cv2.drawContours(frame, c, -1, (255, 255, 0), 1)

        #rect = cv2.minAreaRect(c) # (x,y)(w,h)angle
        rect = cv2.boundingRect(c)
        cv2.rectangle(frame,(rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), (255,255,0), 2)

        #width of basket. Magic number onverts from 16cm to 25cm.
        #might and will depend on lighting and distance of robot.
        #ideally there should be no difference in calculated distance between aruco and blob.
        if rect[3] > 20:
            return rect[2] * 1.689, rect[0] + rect[2]//2, [], []

    return -1, -1, None, None






if __name__ == '__main__':
    import communication
    throwspeed = 0
    basket = None

    print( "We have OpenCV version " + cv2.__version__ )    #i have 3.3.0
    cap = cv2.VideoCapture(0)
    cap.set(13, 0.40)
    cap.set(14, 0.04)

    ret, frame = cap.read()
    print('Frame shape: ' + str(frame.shape)) #480x640
    print('aruco params: ' + str(parameters))
    print('searching for basket: ' + str(BASKET) )
    adjust = 0

    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret: #can i ignore bad frames?
            continue

        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) is it better on colorframe
        dist, basket, corners, ids = detect_basket(frame)
        frame = aruco.drawDetectedMarkers(frame, corners)
        throwspeed = calculate_thrower_speed(dist)
        if basket >= 0:
            cv2.line(frame, (int(basket), 0), (int(basket),400), (255,255,0), 2)
            cv2.putText(frame, "Dist:" + str(dist), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0) )
            cv2.putText(frame, "Calculated:" + str(throwspeed), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0) )

        cv2.putText(frame, "Adjust:" + str(adjust), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255) )

        h, w = frame.shape[:2]
        print (frame.shape)
        cv2.line(frame, (w//2,100), (w//2,200), (0,0,255),1)


        cv2.imshow('frame', frame)
        keyp = cv2.waitKey(1) & 0xFF

        if keyp == ord('q'):
            communication.set_thrower(0)
            communication.update_comms()

            break
        elif keyp == ord('e'):
            adjust += 1
        elif keyp == ord('d'):
            adjust -= 1


        #elif keyp == ord('s'):
        #    adjust = 0
        #elif keyp == ord('w'):
        #    adjust = 100
        throwspeed = throwspeed + adjust
        communication.set_thrower(throwspeed)
        communication.update_comms()

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
