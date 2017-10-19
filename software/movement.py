

import numpy as np


# (0,0) -----------------------  (600,0)
#   |                               |
#   |                               |
# (0,450) -----------------------(600,450)

def get_command(x, y, radius, fow):

    f1, f2, f3 = calculate_force(x, y, radius, fow)
    s = calculate_speed(radius)
    
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
    
def calculate_force(x, y, radius, fow):
    ax, ay, w = find_directions(x, y, radius, fow)
    
    f1 = 0.58*ax + (-0.33)*ay + 0.33*w
    f2 = (-0.58)*ax + (-0.33)*ay + 0.33*w
    f3 = 0*ax + 0.67*ay + 0.33*w
    
    return f1, f2, f3
    
    
def find_directions(x, y, radius, fow):
    
    if x>299:
        angle = ((x-300)/300)*fow/2
        ax = -1
    elif x>0:
        angle = (x/300)*fow/2 
        ax = 1
    else:
        angle = 5
        ax = 0
        
    if radius>100:
        ay = 0
    elif radius>0:
        ay = 1
    else:
        ay = 0

    return ax, ay, angle*3.14/180
    
    

    
    
