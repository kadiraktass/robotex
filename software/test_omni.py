import serial
import cv2
import time
import math
import communication
port = "/dev/ttyACM0"
communication.send_soon("init")
baud = 9600
 
ser = serial.Serial(port, baud, timeout=1)
    # open the serial port
if ser.isOpen():
     print(ser.name + ' is open...')

def get_command()


while 1:
    m1,m2,m3 = get_command(5, 5, 5, 5,5) 
    ser.write("sm"+":"+m1+":"+m2+":"+m3 + '\n')
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
	    break

    



        
    