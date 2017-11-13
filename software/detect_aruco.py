'''
Plan:

Distance is expressed in pixels, simply distance between two markers.
Converting to centimeters/etc will introduce additional errors.
Location of basket is given in pixels also (on horizontal axis only)


Process of calibration:
Put robot to a distance of 1m, measured from first edge of robot to backplate of basket.
Read distance in pixels, find neccessary speed for thrower, repeat and rinse, derive a function for a curve.
Introduce a quick calibration constant in case field of competition is slightly different.
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
from config import ARUCOWIDTH, ARUCODISTANCE, BASKET

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

#"Corrupt JPEG data: premature end of data segment" with freezing is killing me. I need to recompile again??
def detect_basket( frame ):
    #lists of ids and the corners belonging to each id

    corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
    #found something. Gives None or some numpy array.
    if type(ids) is None or type(corners) is None:
        return [], []

    #but i do not know how numpy arrays work
    corners = corners.tolist()
    ids = ids.tolist()

    found = []
    for i in range(0, len(ids)):
            if ids[i][0] in [ BASKET[0], BASKET[1] ]:
                found.append( corners[i][0] )
                print (corners[i])

    if len(found) > 0:
            print("det:" + str(found))
            dist_between = max(found) - min(found)
            print ("dist:" + dist_between)

    return corners, ids
    #gray = aruco.drawDetectedMarkers(gray, corners)



if __name__ == '__main__':
    print( "We have OpenCV version " + cv2.__version__ )    #i have 3.3.0
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    print('Frame shape: ' + str(frame.shape)) #480x640
    print('aruco params: ' + str(parameters))
    print('searching for basket: ' + str(BASKET) )


    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret: #can i ignore bad frames?
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        corners, ids = detect_basket(gray)

        gray = aruco.drawDetectedMarkers(gray, corners)

        cv2.imshow('frame',gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
