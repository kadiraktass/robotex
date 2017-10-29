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


import cv2  #Seems there are big compatibility issues between versions. So we need to be on same lib.
import cv2.aruco as aruco
import numpy as np

#Important stuff:
_ARUCOWIDTH = 138 #real-life width of aruco marker. Used to calculate distance.


print( "We have OpenCV version " + cv2.__version__ )    #i have 3.3.0
#help( cv2.aruco )
#possible interests:
#calibrateCameraAruco()




#ubuntu has problems with videocapture. Something about ffmpeg support.
#cap = cv2.VideoCapture(0)
#cap = skvideo.io.VideoCapture( 0 )
cap = cv2.VideoCapture(0)
#timeout error: https://stackoverflow.com/questions/12715209/select-timeout-error-in-ubuntu-opencv

#cap.get and gap.set() for resolution




while cap.isOpened():
    # Capture frame-by-frame
    ret, frame = cap.read()
    #print(frame.shape) #480x640

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get( aruco.DICT_ARUCO_ORIGINAL )
    #aruco_dict = aruco.CustomDictionary_generate(25, 5) #original does work.
    parameters =  aruco.DetectorParameters_create()

    #print(parameters)

    '''    detectMarkers(...)
        detectMarkers(image, dictionary[, corners[, ids[, parameters[, rejectedI
        mgPoints]]]]) -> corners, ids, rejectedImgPoints
    '''
        #lists of ids and the corners beloning to each id
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    if len(corners) > 0:
        print(corners)
        print(ids)

    gray = aruco.drawDetectedMarkers(gray, corners)
    gray = aruco.drawDetectedMarkers(gray, rejectedImgPoints)

    #print(rejectedImgPoints)
    # Display the resulting frame
    cv2.imshow('frame',gray)
    if cv2.waitKey(0) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()