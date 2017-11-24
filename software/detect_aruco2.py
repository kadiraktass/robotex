'''
Plan B:

Look for LOWER edge of basket (and it's height on picture),
calculate speeds by lookup table (and not trendline formula)
'''

from __future__ import print_function
import cv2  #Seems there are big compatibility issues between versions. So we need to be on same lib.
import cv2.aruco as aruco
import numpy as np
import config
import time
import imutils

aruco_dict = aruco.Dictionary_get( aruco.DICT_ARUCO_ORIGINAL )
parameters =  aruco.DetectorParameters_create()

TAMBOV = 0
#TODO:
#You cannot rely on finding basket from every frame. Therefore strategy is as follows:
#find basket, select speed, attack, hope for the best.

#TODO: maybe.
#if last dist was None more than 1s ago then we do not see basket.
#if we just saw it, but right now did'nt detect, then skip. Timeout keeps track of shutting down.
#if we just saw it, and keep seeing, then keep short running average to smooth out fluctuations, and slow down gracefullyb
running = [0]*10
last_seen = 0

#Use it for distance, not speed!
def gimme_running_average( current_dist ):
    global running
    global last_seen

    now = time.time()
    if current_dist == -1 or current_dist < 48: #so it doesnt hit a kid if a fly flies around
        if ( now - last_seen) > 1: #Havent seen for some time, start degrading
            running.append(999) #this is distance, in a galaxy far, far away...
            running.pop(0)
        else: #just skip
            pass

    else: #saw the basket
        running.append(current_dist)
        running.pop(0)
        last_seen = now

    print(running)
    ret = np.mean( running )
    if ret == 0:
        return -1
    else:
        return ret


#lookup table:
#as big as needed, but keep ordered by distance (ascending)
#start from far away, headed closer
#RESIZE!!!! Oh hell.
lookup=[
#(distance, throw),
(  0, 999), #0 cannot happen
( 48, 650), #edge of field, max speed, cannot reach anyway

( 60, 520),

( 62, 494),
( 69, 464),

( 95, 336),#
(104, 313),
(118, 287),
(127, 270),
(157, 243),
(204, 224),
(230, 216),
(253, 221), #only straight, wall bounce
(281, 263),
(1000, 0)
#etcetera, upto crazy numbers
]

#print ('\n'.join( lookup ))
# TODO: more tries, plot to chart, look for anomalies, repair
# Look if something can be done about close-range-detection and throw
def calculate_thrower_speed( dist ):
    print("tambov", TAMBOV)
    if dist < 0:
        return 0

    for i in range(0, len(lookup) -1):
        if dist == lookup[i][0]:
            return lookup[i][1]

        if lookup[i][0] <= dist <= lookup[i+1][0]:
            #return int(round((lookup[i][1] + lookup[i][1]) / 2))
            #No, not average. Linear extrapolation, stupid!
            # (y2-y1)/(x2-x1) * (X-x1) + y1
            a = (lookup[i+1][1] - lookup[i][1]) / (lookup[i+1][0] - lookup[i][0])
            dx = dist - lookup[i][0]

            return int( a * dx + lookup[i][1] + TAMBOV )
    return 0


def detect_basket( frame ):
    #lists of ids and the corners belonging to each id

    #corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
    #found something. Gives None or some numpy array.
    #if ids is None:
    #    return fallback_to_blob(frame)
    #try it
    a,b,c,d = fallback_to_blob(frame)
    if a > 0:
        return a,b,c,d

    #else look for aruco
    corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
    if ids is None:
        return -1, -1, None, None


    #when i find rightmost marker, it means basket is a little bit leftwards.
    #ditto for left one. And arithmetic mean if both are visible.
    #oh hell, detection is horrible. Works only under ideal conditions.
    found = []
    dists = []
    basks = []
    BASKET = config.BASKET
    #marker is (vertical_distance, x_of_basket)
    for i in range(0, len(ids)):
            topleft     = corners[i][0][0]
            topright    = corners[i][0][1]
            bottomright = corners[i][0][2]
            bottomleft  = corners[i][0][3]

            height = bottomleft[1] - topleft[1]
            print (topleft, topright, bottomleft, height)

            if ids[i][0] == BASKET[0]: #left marker
                dists.append ( bottomright[1] + height/6 ) #magic numbers found by trial
                basks.append ( topright[0] + height/3 )

            if ids[i][0] ==  BASKET[1]: #right marker
                dists.append ( bottomleft[1] + height/6 )
                basks.append ( topleft[0] - height/3 )

    #if i got both, return arithmetic mean
    if len(dists) == 0:
        return -1, -1, corners, ids

    return int(np.mean(dists)), np.mean(basks), corners, ids




def fallback_to_blob( frame ):
    BASKET = config.BASKET
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, BASKET[2], BASKET[3])
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
    cv2.imshow("mask", mask)
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        c = max(cnts, key=cv2.contourArea)
        cv2.drawContours(frame, c, -1, (255, 255, 0), 1)

        #rect = cv2.minAreaRect(c) # (x,y)(w,h)angle
        rect = cv2.boundingRect(c)
        #ideally there should be no difference in calculated distance between aruco and blob.
        #NB! 50 or less could be already erraneous
        if rect[3] > 20:
            cv2.rectangle(frame,(rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), (255,255,0), 2)
            return rect[1] + rect[3], rect[0] + rect[2]//2, [], []

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
    frame = imutils.resize(frame, width=600) #DOOOH!!!! How it managed, i do not know.

    print('Frame shape: ' + str(frame.shape)) #480x640
    print('aruco params: ' + str(parameters))
    print('searching for basket: ' + str(config.BASKET) )
    adjust = 0

    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret: #can i ignore bad frames?
            continue

        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) is it better on colorframe
        dist, basket, corners, ids = detect_basket(frame)
        frame = aruco.drawDetectedMarkers(frame, corners)

        runnin_dist = gimme_running_average(dist)
        throwspeed = calculate_thrower_speed(runnin_dist)
        throwspeed += adjust

        if basket >= 0:
            cv2.line(frame, (int(basket), 0), (int(basket),400), (255,255,0), 2)
            cv2.line(frame, (250, dist), (350, dist), (255,255,0), 2)
            cv2.putText(frame, "Dist:" + str(round(runnin_dist)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255) )
            cv2.putText(frame, "Calculated:" + str(throwspeed), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0) )

        cv2.putText(frame, "Adjust:" + str(adjust), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255) )
        cv2.putText(frame, "Speed:" + str(throwspeed), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255) )

        communication.set_thrower(throwspeed)
        communication.update_comms()

        h, w = frame.shape[:2]
        print (frame.shape)
        cv2.line(frame, (w//2,100), (w//2,200), (0,0,255),1)


        cv2.imshow('frame', frame)
        keyp = cv2.waitKey(1) & 0xFF

        if keyp == ord('q'):
            communication.send_now("st:0")

            break
        elif keyp == ord('e'):
            adjust += 2
        elif keyp == ord('d'):
            adjust -= 2


        #elif keyp == ord('s'):
        #    adjust = 0
        #elif keyp == ord('w'):
        #    adjust = 100


    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
