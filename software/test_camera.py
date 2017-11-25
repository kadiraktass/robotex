#only show what camera sees, nothing more
import cv2
from config import *

camera = cv2.VideoCapture( cameranum )
camera.set(13, 0.40) #hue
camera.set(14, 0.04)


while True:
    (grabbed, frame) = camera.read()
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
