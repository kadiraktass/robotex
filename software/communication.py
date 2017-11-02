#
#  I try to implement a lazy communication module - one that doesn't flood the pipes.
#  Wont send any repeating commands (maybe needs ack of some kind), doesn't send too fast,
#  one that prioritizes some commands over another and one that keeps connection open despite occasional drops or loss of sync.
#
#  First priority is movement commands and RF-module.
# 9600 bps means approx 1kBps = 1B per millisecond - which is very little. Why 9600? Because it should be bomb-proof.
# we need atleast 50ms delay (Wut? really??) between transmissions to be on a safe side.

# it is recommended to only import neccessary functions from here (id do not have time nor skills for OOP or etc)

import serial
import time
from config import *

FIELD_ID = 'A'
ROBOT_ID = 'Z'
FAILSAFE = True  #would be nice if firmware detects loss of connection and pulls brakes


#should be private
last_command = ''
pending_commands = []
last_time = 0

def millis():
    return int( time.clock() * 1000 )

#call this in a main loop (or rewrite into separate Thread - would be nice)
def update_comms():
    now = millis()
    if (now - last_time) > 0 and len(pending_commands) > 0:
        send_now( pending_commands.pop(0) )
        last_time = now

    pass

#some things do need immediate sending
def send_now( message ):
    pass

def set_motors(m1, m2, m3):
    pass


ser = serial.Serial(serialport, 9600, timeout=None)
while True:
      print( ser.readline() )
