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


def setup_trackbars(range_filter):
    cv2.namedWindow("Trackbars", 0)

    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255

        for j in range_filter:
            cv2.createTrackbar("%s_%s" % (j, i), "Trackbars", v, 255, callback)


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


def main():
    #args = get_arguments()
    colorvals = pickle.load( open( "color_values.pkl", "rb" ) )
    active = 'ball'
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
    camera.set(13, 0.4)
    camera.set(14, 0.04)
    setup_trackbars(range_filter)

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

        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(range_filter)
        #print ("({0}, {1}, {2}) ({3}, {4}, {5})".format(v1_min, v2_min, v3_min,    v1_max, v2_max, v3_max))

        thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))

        #if args['preview']:
        if False:
            preview = cv2.bitwise_and(image, image, mask=thresh)
            cv2.imshow("Preview", preview)
        else:
            cv2.putText(image, "Active:" + active, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0) )
            cv2.imshow("Original", image)
            cv2.imshow("Thresh", thresh)

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

        if key == '1':
            active = 'ball'
        if key == '2':
            active = 'basket_magenta'
        if key == '3':
            active = 'basket_blue'
        if key == '4':
            active = 'carpet'




if __name__ == '__main__':
    main()
