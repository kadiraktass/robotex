import numpy as np
import time
import math
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
    GO_TO_MID = 6

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

    return wheelAngularSpeedMainboardUnits1, wheelAngularSpeedMainboardUnits3, wheelAngularSpeedMainboardUnits2, thrower_speed

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
    if basket_x>300:
        basketPosOnRight = 1
    elif basket_x>0:
        basketPosOnRight = -1

    basketInCenter = abs(basket_x  - 300) <= 20
    seesBall = ball_x != -1

    if activeState != State.FIND_BALL:
        if (ball_x == -1 and activeState != State.GO_TO_MID):
            activeState = State.FIND_BALL
            findBallStartTime = time.time()
    else:
        if time.time() - findBallStartTime > 2:
            activeState = State.GO_TO_MID

    if activeState  != State.GRAB_BALL:
        if (ball_x == -1):
            activeState = activeState
        else:
            #I'm trying a little jerk in another direction
            #if activeState == State.FIND_BALL: #Was searching for ball, did glimpse it
            #Nooo, It does find and aim for ball perfectly while it is closer.
            #Therefore problem lies in detecting the ball.

            activeState = State.DRIVE_TO_BALL

        if ball_x != -1 and basketInCenter:
            activeState = State.DRIVE_TO_BALL

        if orangeArea < 110000:
            activeState = State.RUN_FROM_BORDER
            print("FLEEEEE!!!! ")

        if not basketInCenter and ball_y >= 380:
            activeState = State.ROTATE_AROUND_BALL

        if basketInCenter and ball_y >= 420:
            activeState = State.GRAB_BALL
            grabBallStartTime = time.time()

        #if orangeArea < 100000:
        #    activeState = State.RUN_FROM_BORDER

    else:
        if time.time() - grabBallStartTime > 2:
            activeState = State.FIND_BALL

    if (activeState == State.FIND_BALL):
        rotSpeed = -2.5

    elif (activeState == State.DRIVE_TO_BALL):
        rotSpeed = 1.5*(ball_x - 300) * 1 / 300
        ySpeed = 1.5*0.5 * abs(430 - ball_y) / 430

    elif (activeState == State.ROTATE_AROUND_BALL):
        if (basket_x == -1):
            rotSpeed = 4 * 0.5 * basketPosOnRight               #rotate to the right if basket left from the right side of the screen
            xSpeed = 4 * -0.1* basketPosOnRight
        else:
            rotSpeed = (basket_x - 300) * 0.5 / 300
            xSpeed = (basket_x - 300) * -0.1 / 300

    elif (activeState == State.GRAB_BALL):
            ySpeed = 0.05 #was 0.05
            rotSpeed = (basket_x - 300) * 0.2 / 300
            thrower_speed = calculate_thrower_speed(basket_dist)

    elif (activeState == State.RUN_FROM_BORDER):
        rotSpeed = -2.5

    elif (activeState == State.GO_TO_MID):
        if (basket_x == -1):
            rotSpeed = -2.5 * basketPosOnRight               #rotate to the right if basket left from the right side of the screen
        else:
            rotSpeed = (basket_x - 300) * 0.5 / 300
            if(basket_x-300)<20 and basketPosOnRight:                              #TODO: test for a better value
                xSpeed = 1                                  #TODO: test for a better value
            elif(basket_x-300)<20 and not basketPosOnRight:
                xSpeed = -1
            else:
                xSpeed = 0

            if time.time() - findBallStartTime > 3:
                activeState = State.FIND_BALL



    return xSpeed, ySpeed, rotSpeed, angular_v, thrower_speed
