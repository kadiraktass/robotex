import serial
import time

port = "COM3"
baud = 9600
 
ser = serial.Serial(port, baud, timeout=1)
if ser.isOpen():
     print(ser.name + ' is open...')

while 1:

	input = raw_input(">> ")
	
	ser.write(input + '\r\n')
	out = ''
