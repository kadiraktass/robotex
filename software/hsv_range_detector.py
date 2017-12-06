#!/usr/bin/env python
# -*- coding: utf-8 -*-

# USAGE: You need to specify a filter and "only one" image source
#
# (python) range-detector --filter RGB --image /path/to/image.png
# or
# (python) range-detector --filter HSV --webcam

from __future__ import print_function
import cv2
import argparse
from operator import xor
import pickle


def callback(value):
    pass


def setup_trackbars(range_filter, colorvals, active):
    cv2.namedWindow("Trackbars", 0)

    for i in ["MIN", "MAX"]:
        if active in colorvals:
            colors = colorvals[active][0 if i == "MIN" else 1]
        else:
            v = 0 if i == "MIN" else 255
            colors = (v, v, v)

        print(colors)
        for j in range(0, len(range_filter)):
            cv2.createTrackbar("%s_%s" % (range_filter[j], i), "Trackbars", colors[j], 255, callback)


def get_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--filter', required=False,
                    help='Range filter. RGB or HSV', nargs='?',
                    const='HSV')
    ap.add_argument('-i', '--image', required=False,
                    help='Path to the image')
    ap.add_argument('-w', '--webcam', required=False,
                    help='Use webcam', action='store_true')
    ap.add_argument('-p', '--preview', required=False,
                    help='Show a preview of the image after applying the mask',
                    action='store_true')
    args = vars(ap.parse_args())

    if not xor(bool(args['image']), bool(args['webcam'])):
        ap.error("Please specify only one image source")

    if not args['filter'].upper() in ['RGB', 'HSV']:
        ap.error("Please speciy a correct filter.")

    return args


def get_trackbar_values(range_filter):
    values = []

    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)

    return values


picked = None
#mouse callback for picking a pixel value.
def pick(event, x, y, flags, param):
    global picked
    if event == cv2.EVENT_LBUTTONUP:
        picked = (x, y)


def main():
    global picked
    #args = get_arguments()
    try:
        colorvals = pickle.load( open( "color_values.pkl", "rb" ) )
    except:
        try:
            colorvals = pickle.load( open( "color_values.pkl.bak", "rb" ) )
        except:
            raise
        colorvals = {'ball':((0,0,0),(255,255,255))}
    active = 'ball'

    cv2.namedWindow("Thresh")
    cv2.moveWindow("Thresh", 20,20)
    cv2.namedWindow("Original")
    cv2.moveWindow("Original", 500,20)
    cv2.setMouseCallback("Original", pick)

    cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Trackbars", 400, 300)
    cv2.moveWindow("Trackbars", 400,400)






    print ("Loaded: " + str(colorvals))
    '''
    { 'ball' : ( (0,0,0),  (255,255,255) )
      'basket_magenta' : ...
    }
    '''

    range_filter = 'HSV' #args['filter'].upper()

    #if args['image']:
    #    image = cv2.imread(args['image'])

    #    if range_filter == 'RGB':
    #        frame_to_thresh = image.copy()
    #    else:
    #        frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    #else:
    camera = cv2.VideoCapture(0)
    camera.set(13, 0.40) #was 0.4
    camera.set(14, 0.04)

    setup_trackbars(range_filter, colorvals, active)
    while True:
        #if args['webcam']:
        if True:
            ret, image = camera.read()

            if not ret:
                break

            if range_filter == 'RGB':
                frame_to_thresh = image.copy()
            else:
                frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        #does blur help in deflickering? Not really.
        #image = cv2.blur(image, (3,3)) #does not help
        #image = cv2.GaussianBlur(image,(15,15),0) #slightly better
        image = cv2.medianBlur(image, 15) #might help? But only a littleself.
        #image = cv2.fastNlMeansDenoisingColored(image,None,10,10,7,21) - way too slow
        #Additionally, there is option to route vide stream through ffmpeg encoding, which also knows how to remove noise well
        #vlc "http://192.168.180.60:82/videostream.cgi?user=admin&pwd=" --sout "#transcode{vcodec=mp2v,vb=800,scale=1,acodec=mpga,ab=128,channels=2,samplerate=??44100}:duplicate{dst=rtp{sdp=rtsp://:8554/output.mpeg},dst=display}" --sout-keep
        #cap=cv2.VideoCapture("rtsp://:8554/output.mpeg")

        #study accumulateWeighted
        #"An approach might be to let the camera 'learn' what the background looks like with no object. "
        #"https://stackoverflow.com/questions/24379456/detecting-an-approaching-object"

        if picked:
            print ("PICKED!")
            c = frame_to_thresh[picked[1]][picked[0]]
            print(c)
            setup_trackbars(range_filter, {active: ((c[0]-5,c[0]-20,0,),(c[0]+5,c[1]+20,255))}, active)
            picked = None


        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(range_filter)
        #print ("({0}, {1}, {2}) ({3}, {4}, {5})".format(v1_min, v2_min, v3_min,    v1_max, v2_max, v3_max))

        thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))
        #thresh = cv2.erode(thresh, None, iterations=2)
        #thresh = cv2.dilate(thresh, None, iterations=2)

        #try to show what robot actually sees:
        #TODO: needs unified place and actual algorithm. Possibly a way to fine tune eroding or choosing some other or...
        if active == 'ball':
            mask = cv2.erode(thresh, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)[-2]
            for c in cnts:
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                cv2.circle(image, (int(x), int(y)), int(radius),(0, 255, 255), 2)

            if len(cnts) > 0:
                c = max(cnts, key=cv2.contourArea)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])) #why do we not use enclosingCircle's center?
                cv2.circle(image, center, 10,(0, 0, 255), -1)

        elif active == 'basket_blue' or active == 'basket_magenta':
            mask = cv2.erode(thresh, None, iterations=3)
            mask = cv2.dilate(mask, None, iterations=3)
            cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
            if len(cnts) > 0:
                c = max(cnts, key=cv2.contourArea)
                cv2.drawContours(image, c, -1, (255, 255, 0), 1)
            rect = cv2.boundingRect(c)
            if rect[3] > 20:
                cv2.rectangle(image,(rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), (255,255,0), 2)

        #if args['preview']:
        if False:
            preview = cv2.bitwise_and(image, image, mask=thresh)
            cv2.imshow("Preview", preview)
        else:
            cv2.putText(image, "Configure:" + active, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0) )
            cv2.putText(image, "(Press 's' for save; '1'..'4' to select what to configure)", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,200,0) )
            cv2.imshow("Thresh", thresh)
            cv2.imshow("Original", image)

        key = cv2.waitKey(1) & 0xFF
        key = chr(key).lower()

        if key == 'q':
            break

        if key == 's':
            print('save here')
            f = open('color_values.pkl', 'wb')
            colorvals[active] = ((v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))
            pickle.dump( colorvals, f)
            f.close()
            f = open('color_values.pkl.bak', 'wb')
            colorvals[active] = ((v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))
            pickle.dump( colorvals, f)
            f.close()

        if key == '1':
            active = 'ball'
            setup_trackbars(range_filter, colorvals, active)
        if key == '2':
            active = 'basket_magenta'
            setup_trackbars(range_filter, colorvals, active)
        if key == '3':
            active = 'basket_blue'
            setup_trackbars(range_filter, colorvals, active)
        if key == '4':
            active = 'carpet'
            setup_trackbars(range_filter, colorvals, active)




if __name__ == '__main__':
    main()
