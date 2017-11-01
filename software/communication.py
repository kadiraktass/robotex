#
#
#
#
import serial
from config import *



ser = serial.Serial(serialport, 9600, timeout=None)
while True:
      print( ser.readline() )
