

import numpy as np
import time
import math

# (0,0) -----------------------  (600,0)
#   |                               |
#   |                               |
# (0,450) -----------------------(600,450)

def get_command(x, y, radius, fow):

    wheelLinearVelocity1, wheelLinearVelocity2, wheelLinearVelocity3 = calculate_speed(x, y, radius, fow,input)
    
    wheelSpeedToMainboardUnits = 91         #TODO: Determine the exact value
    
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
    
    cmd = 'sd'+ ':' + temp1 + ':'+ temp3+ ':'+ temp2
    return cmd

def calculate_speed(x, y, radius, fow,input):

    movement_angle, angular_v, desired_speed = find_directions(x, y, radius, fow)
    robotDirectionAngle= movement_angle         #rad
    robotAngularVelocity= angular_v
    
    wheelDistanceFromCenter= 0.126   #meter
    robotSpeed= desired_speed                #m/s
    wheelAngle1=-60*3.14/180                   #rad
    wheelAngle2=60*3.14/180                    #rad
    wheelAngle3=0                    #rad

    wheelLinearVelocity1 = robotSpeed * math.cos(robotDirectionAngle - wheelAngle1) + wheelDistanceFromCenter * robotAngularVelocity
    wheelLinearVelocity2 = robotSpeed * math.cos(robotDirectionAngle - wheelAngle2) + wheelDistanceFromCenter * robotAngularVelocity
    wheelLinearVelocity3 = robotSpeed * math.cos(robotDirectionAngle - wheelAngle3) + wheelDistanceFromCenter * robotAngularVelocity   
    
    return wheelLinearVelocity1, wheelLinearVelocity2, wheelLinearVelocity3
    
    
def find_directions(x, y, radius, fow):
    
    if x>350:               #TODO: Determine the exact value
        #turn right until x 290 310
        movement_angle = 0
        desired_speed = 0
#<<<<<<< HEAD
        angular_v = 30        #TODO: Determine the exact valu
    elif 250>x>0:                   #TODO: Determine the exact value
        #turn left until x 290 310
        movement_angle = 0
        desired_speed = 0
        angular_v = -90        #TODO: Determine the exact value
    elif 0>x:
        #turn right until x is detected
        movement_angle = 0
        desired_speed = 0
        angular_v = 90        #TODO: Determine the exact value
#>>>>>>> 25060d1105aa173c4720042b388a30f73a361e7e
    else:
        movement_angle = 90
        if radius <10:  #TODO: Determine the exact value
            desired_speed = 0   #TODO: Determine the exact value
        elif radius<50: #TODO: Determine the exact value
            desired_speed = 0.4 #TODO: Determine the exact value
        elif radius<300:    #TODO: Determine the exact value
            desired_speed = 0.4  #TODO: Determine the exact value
        else:
            desired_speed = 0  #TODO: Determine the exact value
        angular_v = 0
        
    return movement_angle*3.14/180, angular_v*3.14/180, desired_speed
    
    

    
    
