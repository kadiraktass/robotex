import movement
import math

print(movement.calculateWheelSpeed(1, movement.wheelAngle3, 0, 0))

print(movement.calculate_speeds_from_xy(1, 0, 0))
print(movement.calculate_speeds_from_xy(math.sqrt(2) / 2, math.sqrt(2) / 2, 0))
print(movement.calculate_speeds_from_xy(0, 1, 0))

print(movement.calculate_speeds_from_angle(1, 45 * math.pi / 180 , 0))

print('sm:{0}:{1}:{2}'.format(int(-78.84), int(18.29), int(-1.19595)))