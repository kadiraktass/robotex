#
#  I try to implement a lazy communication module - one that doesn't flood the pipes.
#  Wont send any repeating commands (maybe needs ack of some kind), doesn't send too fast,
#  one that prioritizes some commands over another and one that keeps connection open despite occasional drops or loss of sync.
#
#  First priority is movement commands and RF-module.
# 9600 bps means approx 1kBps = 1B per millisecond - which is very little. Why 9600? Because it should be bomb-proof.
# we need atleast 50ms delay (Wut? really??) between transmissions to be on a safe side.
# https://pythonhosted.org/pyserial/pyserial_api.html
# it is recommended to only import neccessary functions from here (id do not have time nor skills for OOP or etc)

# referee module is wacky. One program only sends, very well, other program, serial monitori, only receives.

# Main logic should need from here only functions:
# update_comms() (to be polled in main loop);
# set_motors(); set_thrower()
# and possibly send_soon()

import serial
import time
from config import *



#should be private
last_command = ''
pending_commands = []  #FIFO buffer. Add to the end, and pop from beginning.
last_time = 0
forced_delay = 50 #millis between sends

ser = serial.Serial(serialport, 9600, timeout=0.2, write_timeout=0.1, dsrtr=True)


def set_motors(m1, m2, m3):
    if not BRAKES_ON:
        t = 'sm:{0}:{0}:{0}'.format(m1, m2, m3)
        send_soon(t)


#todo: would be nice to input distance in centimeters and get proper correlated speed for thrower
def set_thrower(sp):
    if not BRAKES_ON:
        t = 'st:{0}'.format(sp)
        send_soon(t)


#some things need immediate sending
def send_now( message ):
    if ser.out_waiting() > 0:
        ser.flushOutput()  #whatewer there was, it wasnt important anyway
        ser.write('\n')

    return ser.write( message + '\n')
    #write() is blocking by default, unless write_timeout is set. Returns number of bytes written


#most things can wait a bit
def send_soon( message ):
    #if we already have same command in queue, then we will overwrite it.
    if len( pending_commands ) > 0 and pending_commands[-1].startswith( message[0:2] ):
        pending_commands[-1] = message
    else
        pending_commands.append( message )
    return True


#call this in a main loop (or rewrite into separate Thread - would be nice)
def update_comms():
    now = millis()
    if (now - last_time) >= forced_delay and len(pending_commands) > 0:
        send_now( pending_commands.pop(0) )
        last_time = now

    #todo:see if there are something incoming from robot, read them all
    if ser.in_waiting() > 0:
        read_from_robot()

    return True


def read_from_robot():
    while ser.in_waiting() > 0:
        t = ser.readline() #timeout is long enough - in no way should it snip something
        parse_incoming_message( t )
    return True


# mainboard doesnt send much useful information
# set failsade, send ack where appropriate
def parse_incoming_message ( message ):
    #what referee has to say?
    if message.startswith('<ref:'):
        package = message[5:-1]
        print ( package )

        if package[0] == 'a' and (len(package) >= 12 or package[-1] == '-'): #seems legit
            fid, rid, com = package[1], package[2], package[3: package.find('-') ]
            if com not in ['PING','START','STOP']:
                print ' ..garbage\n'
                return False

            #else recognizable command
            if fid == FIELD_ID and rid in [ROBOT_ID, 'X']:
                if rid == ROBOT_ID:
                    send_now( 'a' + fid + rid + 'ACK------') #PING and personal commands must be answered

                if com == 'START':
                    BRAKES_ON = False
                    send_soon( 'st:50' )
                    send_soon( 'r:0' )
                    print ("Houston, all systems green...")

                elif com == 'STOP':
                    BRAKES_ON = True
                    pending_commands = []
                    send_now( 'sm:0:0:0' )
                    send_soon ( 'st:0' )
                    send_soon ( 'r:1' ) #red led on
                    print ("BRAKES, BRAA-AAKES!!!!!")
    return True


def millis():
    return int( time.clock() * 1000 )


#todo: when called as main program: provide serial monitoring and debugging interface
if __name__ == "__main__":
    print ('Lets see if we can communicate with robot.')

    while True:
        update_comms()

    ser.close()
