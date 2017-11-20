

import numpy as np
import time
import math
from detect_aruco import calculate_speed as set_thrower_speed

# (0,0) -----------------------  (600,0)
#   |                               |
#   |                               |
# (0,450) -----------------------(600,450)

i= 0
j= 0
state = 1
thrower_speed = 0
rotate_r=0
stop_rotate = 0
rotate_speed = 0
last_basket_x = -1
def get_rotate_speed(last_basket_x, ball_x):
    global rotate_speed
    global stop_rotate
    print("abs(basket_x - ball_x= ",abs(last_basket_x - ball_x))
    print("last_basket_x = ", last_basket_x)
    if abs(last_basket_x-ball_x)>100:
        rotate_speed = 18
        stop_rotate = 0
    elif abs(last_basket_x-ball_x)>50:
        rotate_speed = 12
        stop_rotate = 0
    elif abs(last_basket_x-ball_x)>6:
        rotate_speed = 3
        stop_rotate= 0
    elif 5>abs(last_basket_x-ball_x):
        rotate_speed = 0
        stop_rotate = 1
    return rotate_speed, stop_rotate

def aim_basket(last_basket_x, ball_x):
    global rotate_r
    if (last_basket_x>=300):
        rotate_r = 1
    elif(last_basket_x<300):
        rotate_r = -1
    rotate_speed,stop_rotate = get_rotate_speed(last_basket_x, ball_x)
    return rotate_r, rotate_speed, stop_rotate


def get_command(ball_x, ball_radius, basket_x, basket_dist):

    wheelLinearVelocity1, wheelLinearVelocity2, wheelLinearVelocity3, thrower_speed,rotate, rotate_speed = calculate_speed(ball_x, ball_radius, basket_x, basket_dist)

    wheelSpeedToMainboardUnits = 91         #TODO: Determine the exact value
    print("rotate",rotate)
    wheelAngularSpeedMainboardUnits1 = wheelLinearVelocity1 * wheelSpeedToMainboardUnits
    wheelAngularSpeedMainboardUnits2 = wheelLinearVelocity2 * wheelSpeedToMainboardUnits
    wheelAngularSpeedMainboardUnits3 = wheelLinearVelocity3 * wheelSpeedToMainboardUnits
    if rotate == 0:
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
    elif rotate==1:
        temp1 = 0
        temp2 = 0
        temp3 = rotate_speed
    else:
        temp1 = 0
        temp2 = 0
        temp3 = -rotate_speed
    #cmd = 'sm'+ ':' + temp1 + ':'+ temp3+ ':'+ temp2        #add thrower speed thrower_speed

    return temp1, temp3, temp2, thrower_speed

def calculate_speed(ball_x, ball_radius, basket_x, basket_diag):

    movement_angle, angular_v, desired_speed, thrower_speed,rotate,rotate_speed = find_directions(ball_x, ball_radius, basket_x, basket_diag)
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

    return wheelLinearVelocity1, wheelLinearVelocity2, wheelLinearVelocity3, thrower_speed,rotate,rotate_speed

def get_angular_speed(ball_x):
    angular_v = abs(ball_x-300)*100/300
    if 5>angular_v>0:
        angular_v = 5
    return angular_v

def find_directions(ball_x, ball_radius, basket_x, basket_dist):

    if basket_x>0:
        last_basket_x = basket_x
    else:
        last_basket_x = last_basket_x
    global last_basket_x
    global rotate_speed
    global stop_rotate
    global state
    global thrower_speed
    global j
    global i
    global rotate_r
    if ball_x>315:               #TODO: Determine the exact value
        #turn right until x 290 310
        movement_angle = 0
        desired_speed = 0
        angular_v = get_angular_speed(ball_x)	#30        #TODO: Determine the exact value
        thrower_speed = 0
        state = 1
        rotate_r = 0

    elif 285>ball_x>0:                   #TODO: Determine the exact value
        #turn left until x 290 310
        movement_angle = 0
        desired_speed = 0
        angular_v =-1*get_angular_speed(ball_x) #-90        #TODO: Determine the exact valueW
        thrower_speed = 0
        state = 1
        rotate_r = 0

    elif 0>ball_x:
        #turn right until x is detected
        movement_angle = 0
        desired_speed = 0
        angular_v = 180        #TODO: Determine the exact value
        thrower_speed = 0
        state = 1
        rotate_r = 0

    else: #BALL HAS TO BE IN THE CENTER
        print("state= ",state)
        print("i= ",i)
        print("j= ",j)
        print("ball_radius= ",ball_radius)
        print("basket_x= ",basket_x)
        print("ball_x= ",ball_x)
        print("basket_dist= ", basket_dist)
        #reached to the ball, stop, set thrower speed, shoot
        if ball_radius > 26 :  #TODO: Determine the exact value
            #FINDING THE BASKET
            if(state == 1):
                movement_angle = 0
                desired_speed = 0
                angular_v = 0
                state = 1
                #if(abs(basket_x - ball_x) < 10): #if(350>basket_x>250):
                if(stop_rotate == 0):
                    rotate_r, rotate_speed  , stop_rotate = aim_basket(last_basket_x,ball_x)
                    print("rotate_Speed = ", rotate_speed)
                    print("stop_rotate = ", stop_rotate)
                else:
                    rotate_r = 0
                    state = 2

            #BASKET HAS BEEN FOUND, ALIGNED, STARTING TO THROW
            elif(state == 2):          #set thrower speed
                thrower_speed = set_thrower_speed(basket_dist) #*3/2
                stop_rotate = 0
                movement_angle = 0
                desired_speed = 0
                angular_v = 0
                rotate_r = 0
                i = i + 1
                if(i > 10):             #TODO: Determine the exact value    #wait until thrower motor reaches desired speed
                    state = 3
                    i = 0
                else:
                    state = 2

            #go forward until the ball is shooted
            #TODO: keep aiming for basket
            elif(state == 3):
                thrower_speed = set_thrower_speed(basket_dist) #H: adjust while edging closer also
                desired_speed = 0.2     #TODO: Determine the exact value
                movement_angle = 90
                angular_v = 0
                rotate_r = 0
                i = i + 1

                if(i > 300):             #TODO: Determine the exact value
                    state = 1
                    i = 0
                else:
                    state = 3

        elif ball_radius >20: #TODO: Determine the exact value
            movement_angle = 90
            desired_speed = 0.1 #TODO: Determine the exact value
            angular_v = 0
            thrower_speed = 0
            state = 1
            rotate_r = 0
        elif ball_radius >0:    #TODO: Determine the exact value
            movement_angle = 90
            desired_speed = 0.4  #TODO: Determine the exact value
            thrower_speed = 0
            state = 1
            angular_v = 0
            rotate_r = 0
        else:
            desired_speed = 0  #TODO: Determine the exact value
            angular_v = 0
            movement_angle = 0
            thrower_speed = 0
            state = 1
            rotate_r = 0
    return movement_angle*3.14/180, angular_v*3.14/180, desired_speed, thrower_speed, rotate_r, rotate_speed
