import serial
import cv2
import time
import math
def get_command(x, y, radius, fow,input):

    wheelLinearVelocity1, wheelLinearVelocity2, wheelLinearVelocity3 = calculate_speed(x, y, radius, fow,input)
    wheelSpeedToMainboardUnits = 91
    wheelAngularSpeedMainboardUnits1 = wheelLinearVelocity1 * wheelSpeedToMainboardUnits
    wheelAngularSpeedMainboardUnits2 = wheelLinearVelocity2 * wheelSpeedToMainboardUnits
    wheelAngularSpeedMainboardUnits3 = wheelLinearVelocity3 * wheelSpeedToMainboardUnits
    
    temp1 = str(abs(int(wheelAngularSpeedMainboardUnits1)))
    while len(temp1) < 3:
        temp1 = '0' + temp1
    
    temp2 = str(abs(int(wheelAngularSpeedMainboardUnits2)))
    while len(temp2) < 3:
        temp2 = '0' + temp2
    
    temp3 = str(abs(int(wheelAngularSpeedMainboardUnits3)))
    while len(temp3) < 3:
        temp3 = '0' + temp3
        
    if wheelAngularSpeedMainboardUnits1 < 0:
        temp1 = '-' + temp1
    else:
        temp1 = '0' + temp1
    
    if wheelAngularSpeedMainboardUnits2 < 0:
        temp2 = '-' + temp2
    else:
        temp2 = '0' + temp2

    if  wheelAngularSpeedMainboardUnits3 < 0:
        temp3 = '-' + temp3
    else:
        temp3 = '0' + temp3
    
    cmd = 'a'+ temp1 + '|'+ temp3+ '|'+ temp2
    print(cmd)
    return cmd
    

def calculate_speed(x, y, radius, fow,input):
    #ax, ay, w = find_directions(x, y, radius, fow,input)
    input = raw_input(">> ")
    print(int(input))
    wheelDistanceFromCenter= 0.126   #meter
    robotSpeed= 0.5                  #m/s
    robotDirectionAngle= int(input)*3.14/180 #1.57        #rad
    wheelAngle1=-60*3.14/180                   #rad
    wheelAngle2=60*3.14/180                    #rad
    wheelAngle3=0                    #rad
    robotAngularVelocity= 0

    wheelLinearVelocity1 = robotSpeed * math.cos(robotDirectionAngle - wheelAngle1) + wheelDistanceFromCenter * robotAngularVelocity
    wheelLinearVelocity2 = robotSpeed * math.cos(robotDirectionAngle - wheelAngle2) + wheelDistanceFromCenter * robotAngularVelocity
    wheelLinearVelocity3 = robotSpeed * math.cos(robotDirectionAngle - wheelAngle3) + wheelDistanceFromCenter * robotAngularVelocity

    
    
    return wheelLinearVelocity1, wheelLinearVelocity2, wheelLinearVelocity3

port = "COM3"
baud = 9600
 
ser = serial.Serial(port, baud, timeout=1)
    #open the serial port
if ser.isOpen():
     print(ser.name + ' is open...')
 
#i=0;

while 1:

	#input = raw_input(">> ")
	
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



        
    