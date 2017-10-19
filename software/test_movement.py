import serial
import cv2
import time
def get_command(x, y, radius, fow,input):

    f1, f2, f3 = calculate_force(x, y, radius, fow,input)
    s = calculate_speed(70)
    
    temp1 = str(abs(int(f1*s)))
    while len(temp1) < 3:
        temp1 = '0' + temp1
    
    temp2 = str(abs(int(f2*s)))
    while len(temp2) < 3:
        temp2 = '0' + temp2
    
    temp3 = str(abs(int(f3*s)))
    while len(temp3) < 3:
        temp3 = '0' + temp3
        
    if f1 < 0:
        temp1 = '-' + temp1
    else:
        temp1 = '0' + temp1
    
    if f2 < 0:
        temp2 = '-' + temp2
    else:
        temp2 = '0' + temp2

    if  f3 < 0:
        temp3 = '-' + temp3
    else:
        temp3 = '0' + temp3
        
    cmd = 'a'+ temp3 + '|'+ temp2 + '|'+ temp1
    return cmd
    
def calculate_speed(radius):

    if radius <10:
        speed = 0
    elif radius<50:
        speed = 100
    elif radius<300:
        speed = 50
    else:
        speed = 10
        
    return speed
    
def calculate_force(x, y, radius, fow,input):
    ax, ay, w = find_directions(x, y, radius, fow,input)
    
    f1 = 0.58*ax + (-0.33)*ay + 0.33*w
    f2 = (-0.58)*ax + (-0.33)*ay + 0.33*w
    f3 = 0*ax + 0.67*ay + 0.33*w
    
    return f1, f2, f3
    
    
def find_directions(x, y, radius, fow,input):
    if input == 'a':
        ax = -1
        ay = 0
        angle = 0
    elif input == 's':
        ax = 0
        ay = -1
        angle = 0
    elif input == "d":
        ax = 1
        ay = 0
        angle = 0
    elif input == "w":
        ax = 0
        ay = 1
        angle = 0
    elif input == "e":
        ax = 1
        ay = 1
        angle = 0
    elif input == "q":
        ax = -1
        ay = 1
        angle = 30
    elif input == "x":
        ax = 0
        ay = 0
        angle = 360 
    else:
        ax = 0
        ay = 0
        angle = 0
    

    return ax, ay, angle*3.14/180
port = "COM3"
baud = 9600
 
ser = serial.Serial(port, baud, timeout=1)
    # open the serial port
if ser.isOpen():
     print(ser.name + ' is open...')
 
i=0;

while 1:

	input = raw_input(">> ")
	
	#if input == 'a':
	#    command = "sd00100"
	#elif input == 's':
	#    command = "sd10100"
	#elif input == "d":
	#    command = "sd20100"
	#else:
	#    command == "sd1000"
	cmd = get_command(0,0,0,0,input)
	ser.write(cmd + '\r\n')
	out = ''
	# let's wait one second before reading output (let's give device time to answer)
	#time.sleep(1)
	#i = i + 1;


command = "sd000"
ser.write(command + '\r\n')



        
    