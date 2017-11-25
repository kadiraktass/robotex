#only show what camera sees, nothing more
import cv2
from config import *

camera = cv2.VideoCapture( cameranum )

hue = 0.4
exp = 0.04


while True:
    camera.set(13, hue)
    camera.set(14, exp)


    (grabbed, frame) = camera.read()


    cv2.putText(frame, "HUE: {}".format(hue),
                        (50, 80), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 1)

    cv2.putText(frame, "EXP: {}".format(exp),
                        (50, 100), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 1)

    cv2.imshow("Frame", frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("e"):
        hue += 0.01

    elif key == ord("d"):
        hue -= 0.01

    elif key == ord("r"):
        exp += 0.01
    elif key == ord("f"):
        exp -= 0.01
