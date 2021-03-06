import numpy as np
import time
import math
import random
from enum import Enum

from detect_aruco2 import calculate_thrower_speed
from communication import millis


# (0,0) -----------------------  (600,0)
#   |                               |
#   |                               |
# (0,450) -----------------------(600,450)

class  State(Enum):
    FIND_BALL = 1
    DRIVE_TO_BALL = 2
    ROTATE_AROUND_BALL = 3
    GRAB_BALL = 4
    RUN_FROM_BORDER = 5

activeState = State.FIND_BALL


thrower_speed = 0
basketPosOnRight = -1
grabBallStartTime = time.time()
findBallStartTime = time.time()



wheelSpeedToMainboardUnits = 18.75 * 64 / (2 * math.pi * 0.035 * 60)
wheelDistanceFromCenter= 0.126   #meter
wheelAngle1 = -60 * math.pi / 180                   #rad
wheelAngle2 = 60 * math.pi / 180                    #rad
wheelAngle3= 180 * math.pi / 180                   #rad
wheelAngles = [wheelAngle1, wheelAngle2, wheelAngle3]


def get_command(ball_x, ball_y, ball_radius, basket_x, basket_dist, orangeArea):

    wheelLinearVelocity1, wheelLinearVelocity2, wheelLinearVelocity3, thrower_speed = calculate_wheelLinerVel(ball_x,ball_y, ball_radius, basket_x, basket_dist,orangeArea)

    wheelAngularSpeedMainboardUnits1 = wheelLinearVelocity1 * wheelSpeedToMainboardUnits
    wheelAngularSpeedMainboardUnits2 = wheelLinearVelocity2 * wheelSpeedToMainboardUnits
    wheelAngularSpeedMainboardUnits3 = wheelLinearVelocity3 * wheelSpeedToMainboardUnits

    x1 = wheelAngularSpeedMainboardUnits1
    x2 = wheelAngularSpeedMainboardUnits2
    x3 = wheelAngularSpeedMainboardUnits3

    #too small of a speed does not make robot move...
    x1 = math.copysign(2, x1) if abs(x1) < 2 else x1
    x2 = math.copysign(2, x2) if abs(x2) < 2 else x2
    x3 = math.copysign(2, x3) if abs(x3) < 2 else x3

    return x1, x3, x2, thrower_speed

def calculateWheelSpeed(robotSpeed, wheelAngle, robotDirectionAngle, robotAngularVelocity):
    return robotSpeed * math.cos(robotDirectionAngle - wheelAngle) + wheelDistanceFromCenter * robotAngularVelocity

def calculate_speeds_from_xy(xSpeed, ySpeed, robotAngularVelocity):
    robotDirectionAngle = math.atan2(ySpeed, xSpeed)
    robotSpeed = math.sqrt(xSpeed * xSpeed + ySpeed * ySpeed)

    return calculate_speeds_from_angle(robotSpeed, robotDirectionAngle, robotAngularVelocity)

def calculate_speeds_from_angle(robotSpeed, robotDirectionAngle, robotAngularVelocity):
    wheelLinearVelocity1 = calculateWheelSpeed(robotSpeed, wheelAngle1, robotDirectionAngle, robotAngularVelocity)
    wheelLinearVelocity2 = calculateWheelSpeed(robotSpeed, wheelAngle2, robotDirectionAngle, robotAngularVelocity)
    wheelLinearVelocity3 = calculateWheelSpeed(robotSpeed, wheelAngle3, robotDirectionAngle, robotAngularVelocity)

    return wheelLinearVelocity1, wheelLinearVelocity2, wheelLinearVelocity3

def calculate_wheelLinerVel(ball_x, ball_y, ball_radius, basket_x, basket_diag,orangeArea):

    xSpeed,ySpeed, rotSpeed, angular_v, thrower_speed = find_directions(ball_x,ball_y,  ball_radius, basket_x, basket_diag,orangeArea)

    robotDirectionAngle = math.atan2(xSpeed, ySpeed)         #rad
    robotAngularVelocity = angular_v

    wheelLinearVelocity1, wheelLinearVelocity2, wheelLinearVelocity3 = calculate_speeds_from_xy(xSpeed, ySpeed, rotSpeed)

    return wheelLinearVelocity1, wheelLinearVelocity2, wheelLinearVelocity3, thrower_speed


def find_directions(ball_x, ball_y, ball_radius, basket_x, basket_dist,orangeArea):
    global activeState
    global grabBallStartTime
    global basketPosOnRight
    global findBallStartTime
    angular_v = 0
    thrower_speed = 0
    xSpeed = 0
    ySpeed = 0
    rotSpeed = 0

    #memorize the basket's last position
    if basket_x>320:
        basketPosOnRight = 1
    elif basket_x>0:
        basketPosOnRight = -1

    basketInCenter = abs(basket_x  - 320) <= 5 #nb!! it depends heavily upon detection quality - unless i keep a running average here too
    seesBall = ball_x != -1

    print("basket_dist = ", basket_dist)
    print("basket_x = ", basket_x)
    print("activeState = ", activeState)
    print("seesBall = ", seesBall)
    print("findBallTime = ", (time.time() - findBallStartTime))


    if activeState  != State.GRAB_BALL:
        if activeState not in (State.FIND_BALL, State.RUN_FROM_BORDER) and not seesBall:
            activeState = State.FIND_BALL
            findBallStartTime = time.time()
        #what is this for? timeout for crazy move. Crazymove should have its own state?!
        elif time.time() - findBallStartTime > 4:
            findBallStartTime = time.time()
            activeState = State.FIND_BALL
        else:
            activeState = State.FIND_BALL

        #if seesBall and basketInCenter: #wut?
        if seesBall:
            activeState = State.DRIVE_TO_BALL

        if orangeArea < 100000: #or basket_dist>377:
            activeState = State.RUN_FROM_BORDER
            print("FLEEEEE!!!! ")

        if not basketInCenter and ball_y >= 400: #380:
            activeState = State.ROTATE_AROUND_BALL

        if basketInCenter and ball_y >= 400: #420:
            activeState = State.GRAB_BALL
            grabBallStartTime = time.time()

    else: #is grabbing
        if time.time() - grabBallStartTime > 3:
            activeState = State.FIND_BALL

    if (activeState == State.FIND_BALL):
        rotSpeed = -1.7
        print("activeState = ", activeState)
        print("findBallStartTime = ", findBallStartTime)
        if time.time() - findBallStartTime > 2.5:
            if(orangeArea> 150000):
                print("find ball directional move = ")
                ySpeed = 0.8
                rotSpeed = -1*random.random() -1
                #findBallStartTime = time.time()

    elif (activeState == State.DRIVE_TO_BALL):
        rotSpeed = 1.5*(ball_x - 320) * 1 / 320
        #ySpeed = 1.5*0.5 * abs(410 - ball_y) / 410 #abs(430 - ball_y) / 430
        ySpeed = 1.5 * abs(410 - ball_y) / 410

    elif (activeState == State.ROTATE_AROUND_BALL):
        if (basket_x == -1): #rotate until basket is seen
            rotSpeed = 3 * 0.5 * basketPosOnRight   #rotate to the right if basket left from the right side of the screen
            xSpeed = 3 * -0.12 * basketPosOnRight
        else: #settle in position - ideally until exactly lined up
            print("settle")
            rotSpeed = (basket_x - 320) * 0.9 / 320
            xSpeed =  (ball_x - 320) * 0.8  / 320
            #xSpeed = max( xSpeed, 0.5)
            #xSpeed =  (basket_x - 320) * -0.11 / 320
            print ("rot, xsp", rotSpeed, xSpeed)


    elif (activeState == State.GRAB_BALL):
            ySpeed = 0.06    #0.05
            rotSpeed = (basket_x - 320) * 0.3 / 320
            thrower_speed = calculate_thrower_speed(basket_dist)

    elif (activeState == State.RUN_FROM_BORDER):
        rotSpeed = -2 #-2.5


    return xSpeed, ySpeed, rotSpeed, angular_v, thrower_speed
