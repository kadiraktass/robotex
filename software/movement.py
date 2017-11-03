

import numpy as np
import time
import math

# (0,0) -----------------------  (600,0)
#   |                               |
#   |                               |
# (0,450) -----------------------(600,450)

i= 0
j= 0
state = 1
thrower_speed = 0

def set_thrower_speed(basket_radius):
    
    thrower_speed = 10      #TODO: Calculate thrower speed here
    
    return thrower_speed
    
def get_command(ball_x, ball_radius, basket_x, basket_diag):

    wheelLinearVelocity1, wheelLinearVelocity2, wheelLinearVelocity3, thrower_speed = calculate_speed(ball_x, ball_radius, basket_x, basket_diag)
    
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
    
    cmd = 'sd'+ ':' + temp1 + ':'+ temp3+ ':'+ temp2        #add thrower speed thrower_speed
    return cmd

def calculate_speed(ball_x, ball_radius, basket_x, basket_diag):

    movement_angle, angular_v, desired_speed, thrower_speed = find_directions(ball_x, ball_radius, basket_x, basket_diag)
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
    
    return wheelLinearVelocity1, wheelLinearVelocity2, wheelLinearVelocity3, thrower_speed
    
    
def find_directions(ball_x, ball_radius, basket_x, basket_diag):
    
    global state
    global thrower_speed
    global j
    global i
    
    if ball_x>350:               #TODO: Determine the exact value
        #turn right until x 290 310
        movement_angle = 0
        desired_speed = 0
        angular_v = 30        #TODO: Determine the exact value
        thrower_speed = 0
        state = 1
        
    elif 250>ball_x>0:                   #TODO: Determine the exact value
        #turn left until x 290 310
        movement_angle = 0
        desired_speed = 0
        angular_v = -90        #TODO: Determine the exact value
        thrower_speed = 0
        state = 1
    elif 0>ball_x:
        #turn right until x is detected
        movement_angle = 0
        desired_speed = 0
        angular_v = 90        #TODO: Determine the exact value
        thrower_speed = 0
        state = 1

    else:
        if ball_radius > 30 :  #TODO: Determine the exact value    #reached to the ball, stop, set thrower speed, shoot
            #print(state)
            #print(thrower_speed)
            if(state == 1):
                #print(j)
                if(j>60):
                #if(basket_diag>0 & 350>basket_x & basket_x>250):        #rotate around the ball until basket is found and it is in the same direction
                    state = 2
                    desired_speed = 0
                    movement_angle = 0
                    angular_v = 0
                else:
                    desired_speed = 0.4         #TODO: Determine the exact value 
                    movement_angle = 180        #TODO: Determine the exact value 
                    angular_v = 0
                    state = 1
                    j = j +1
            elif(state == 2):          #set thrower speed
                thrower_speed = set_thrower_speed(basket_diag)
                movement_angle = 0
                desired_speed = 0
                angular_v = 0
                i = i + 1
                if(i > 50):             #TODO: Determine the exact value    #wait until thrower motor reaches desired speed
                    state = 3
                    i = 0
                else:
                    state = 2
            elif(state == 3):
                desired_speed = 0.4     #TODO: Determine the exact value
                movement_angle = 90
                angular_v = 0
                i = i + 1
                if(i > 20):             #TODO: Determine the exact value    #go forward until the ball is shooted
                    state = 1
                    i = 0
                else:
                    state = 3
            
        elif ball_radius >10: #TODO: Determine the exact value
            movement_angle = 90
            desired_speed = 0.4 #TODO: Determine the exact value
            angular_v = 0
            thrower_speed = 0
            state = 1
        elif ball_radius >0:    #TODO: Determine the exact value
            movement_angle = 90
            desired_speed = 0.4  #TODO: Determine the exact value
            thrower_speed = 0
            state = 1
            angular_v = 0
        else:
            desired_speed = 0  #TODO: Determine the exact value
            angular_v = 0
            movement_angle = 0
            thrower_speed = 0
            state = 1
        
    return movement_angle*3.14/180, angular_v*3.14/180, desired_speed, thrower_speed
    
    

    
    
