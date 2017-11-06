import serial
import time


serdev = '/dev/ttyACM0'
s = serial.Serial(serdev, 9600, parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_TWO,
                                bytesize=serial.EIGHTBITS
)

s.write("helloasd")
s.flush()

time.sleep(1)

while s.inWaiting():
      print (s.read(3))
s.close()