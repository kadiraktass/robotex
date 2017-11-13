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
# set_motors(m1,m2,m3); set_thrower(sp)
# and possibly send_soon(message)
# And you can use it stand-alone.

#
#
#
#



from __future__ import print_function
import serial
import time
from config import serialport, FIELD_ID, ROBOT_ID, BRAKES_ON
import serial.tools.list_ports
import sys

#should be private
last_command = ''
pending_commands = []  #FIFO buffer. Add to the end, and pop from beginning.
last_time = 0
forced_delay = 50 #millis between sends


_port = '' #i am trying autodetection, else takes from config
_baud = 9600
_timeout=0.2
_write_timeout=0.1
_dsrtr=True
_tscts=True
ser = serial.Serial()


def set_motors(m1, m2, m3):
    if not BRAKES_ON:
        t = 'sm:{0}:{1}:{2}'.format(int(m1), int(m2), int(m3))
        send_soon(t)


#todo: would be nice to input distance in centimeters and get proper correlated speed for thrower
def set_thrower(sp):
    if not BRAKES_ON:
        t = 'st:{0}'.format(int(sp))
        send_soon(t)
        print('pending from set_thrower: '+ str(pending_commands))


#some things need immediate sending
def send_now( message ):
    #if ser.outWaiting() > 0:
    #    ser.flushOutput()  #whatewer there was, it wasnt important anyway
    #    ser.write('\n')
    print('SERIAL JUST SENT: ' + message + ', pending: ' + str(pending_commands))

    return ser.write( message + '\n')
    #write() is blocking by default, unless write_timeout is set. Returns number of bytes written


#most things can wait a bit
def send_soon( message ):
    global pending_commands
    #if we already have same command in queue, then we will overwrite it.
    #its not neccessarily the last command
    if len( pending_commands ) > 0:
        for i in range(0, len(pending_commands)):
            if pending_commands[i].startswith( message[0:2] ):
                pending_commands[i] = message
                break
    else:
        pending_commands.append( message )
    return True


#call this in a main loop (or rewrite into separate Thread - would be nice)
def update_comms():
    global last_time, pending_commands

    if open_port():
        now = millis()
        if (now - last_time) >= forced_delay and len(pending_commands) > 0:
            while len(pending_commands) > 0:
                print( "pending: "+ str(pending_commands))
                send_now( pending_commands.pop(0) )
                time.sleep(0.1)
                last_time = now

        #todo:see if there are something incoming from robot, read them all
        if ser.inWaiting() > 0:
            read_from_robot()

    return True


def read_from_robot():

    while ser.inWaiting() > 0:
        t = ser.readline() #timeout is long enough - in no way should it snip something
        t = t.strip()
        if len(t) > 0:
            print('FROM: ' + t)
            parse_incoming_message( t )
    return True


# mainboard doesnt send much useful information
# set failsade, send ack where appropriate
def parse_incoming_message ( message ):
    global BRAKES_ON
    #what referee has to say?
    if message.startswith('<ref:'):
        package = message[5:-1]
        print ( package )

        if package[0] == 'a' and (len(package) >= 12 or package[-1] == '-'): #seems legit
            fid, rid, com = package[1], package[2], package[3: package.find('-') ]
            if com not in ['PING','START','STOP']:
                print ('..garbage\n')
                return False

            #else recognizable command
            if fid == FIELD_ID and rid in [ROBOT_ID, 'X']:
                if rid == ROBOT_ID:
                    send_now( 'rf:a' + fid + rid + 'ACK------') #PING and personal commands must be answered
                    print("ACK sent\n")

                if com == 'START':
                    BRAKES_ON = False
                    send_soon( 'st:40' )
                    send_soon( 'r0' )
                    print ("Houston, all systems green...")

                elif com == 'STOP':
                    BRAKES_ON = True
                    pending_commands = []
                    send_now( 'sm:0:0:0' )
                    send_soon ( 'st:0' )
                    send_soon ( 'r1' ) #red led on
                    print ("BRAKES, BRAA-AAKES!!!!!")
    return True


def millis():
    return int( time.clock() * 1000 )


#from: http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
def detect_serial_ports():
    global _port

    ports = serial.tools.list_ports.comports() #gives list of tuples
    result = [p for p in ports if p[2] != 'n/a']
    result.sort( key=lambda row: (row[2], row[1]) )

    bestguess = [p for p in result if p[2].find('1f00:2012') >= 0]
    if len(bestguess) == 1:
        _port = bestguess
    else:
        _port = serialport
    #yeah, id is one thing, name is another. Well do without.
    #print ("((\n TODO: if guessing is reliable, auto-set config.serialport \n" + str(bestguess) + '\n))\n')

    return result

## try to reconnect if connection lost
def open_port():
    global pending_commands
    detect_serial_ports()

    if not ser.isOpen():
        ser.port = _port
        #ser.baud = _baud
        ser.timeout = _timeout
        ser.write_timeout = _write_timeout

        ser.dsrdtr = _dsrtr
        ser.tscts = _tscts

        try:
            ser.open()
            if ser.isOpen():
                print('Serial port just opened @ '+ _port)
            else:
                if len(pending_commands) > 0:
                    print('Not sent:' + pending_commands.pop(0) )

        except (OSError, serial.SerialException) as e:
                print (e)
                print ('Might help: $ fuser ' + _port)

                if len(pending_commands) > 0:
                    print('Not sent:' + pending_commands.pop(0) )


    return ser.isOpen()


#todo: when called as main program: provide serial monitoring and debugging interface
if __name__ == "__main__":

    # try to open defined port
    print ('Serial version ' + serial.VERSION)
    print ('Lets see if we can communicate with robot?')
    for i in range(0,10):
        open_port()
        if ser.isOpen():
            break
        ser.close()
        print('.', end='')
        sys.stdout.flush()
        time.sleep(1)

    #Orif there is no success then list possible ports and die
    if not ser.isOpen():
        print ('Failed to establish connection. Is config.py correct? ')
        print ('Available ports are:')
        #print (detect_serial_ports() )
        print ('\n'.join ( str(x) for x in detect_serial_ports() ))
        sys.exit(0)

    print ('Ctrl+C lets you write custom command, Ctrl+C twice exits.')
    try:
        while True:
            try:
                update_comms()
            #please note that this is blocking!
            except KeyboardInterrupt:
                print("\n>>-----------------------------------------------------")
                c = raw_input(">>> ")
                if len(c) > 0:
                    send_now( c )
                print("-----------------------------------------------------<<")

    except KeyboardInterrupt:
        ser.close()
        print( 'Bye.')
