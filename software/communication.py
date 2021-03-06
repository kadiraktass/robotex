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
#from config import serialport, FIELD_ID, ROBOT_ID, BRAKES_ON
import config
import serial.tools.list_ports
import sys

#should be private
last_command = ''
pending_commands = []  #FIFO buffer. Add to the end, and pop from beginning.
last_time = 0
forced_delay = 30 #millis between sends
#does not help, still occasional buffer fill.


_port = '' #i am trying autodetection, else takes from config
_baud = 9600
_timeout=0.2
_write_timeout=0.5
_dsrtr=True
_tscts=True
ser = serial.Serial()
lastthrow = 0

def set_motors(m1, m2, m3):
    if not config.BRAKES_ON:
        t = 'sm:{0}:{1}:{2}'.format(int(m1), int(m2), int(m3))
        send_soon(t)


#todo: would be nice to input distance in centimeters and get proper correlated speed for thrower
def set_thrower(sp):
#    a = "st:"+ str(sp)
#    print("thrower command=",a)
#    ser.write("st:"+ str(sp) + '\r\n')
    global lastthrow
    if not config.BRAKES_ON:
        t = 'st:{0}'.format(int(sp))
        #send_soon(t)
        if sp != lastthrow:
            send_now(t)
            lastthrow = sp


#some things need immediate sending
def send_now( message ):
    #Hm, is different in some versions: outWaiting()
    #s = fcntl.ioctl(self.fd, TIOCOUTQ, TIOCM_zero_str)
    #AttributeError: 'Serial' object has no attribute 'fd'
    #if ser.out_waiting > 0:
    #    ser.reset_output_buffer()
    #    ser.write('\n')
    #ser.flushOutput()  #whatewer there was, it wasnt important anyway
    #sleep(.01)
    #    print("FLUSHED, DOWN THE DRAIN")


    if ser.isOpen():
        ser.flushOutput()
        print('SERIAL JUST SENT: ' + message + ', pending: ' + str(pending_commands))
        try:
            return ser.write( message + '\n')
            #serial write timeout...
        except:
            print ('LIFE SUCKS! Oh and you just lost a packet for no good reason.')
            ser.flushOutput()  #whatewer there was, it wasnt important anyway
            time.sleep(0.5)
            return False
    #write() is blocking by default, unless write_timeout is set. Returns number of bytes written


#most things can wait a bit
def send_soon( message ):
    global pending_commands
    #if we already have same command in queue, then we will overwrite it.
    #its not neccessarily the last command
    doineedtoappend = True
    if len( pending_commands ) > 0:
        for i in range(0, len(pending_commands)):
            if pending_commands[i].startswith( message[0:2] ):
                pending_commands[i] = message
                doineedtoappend = False
                break

    if doineedtoappend == True:
        pending_commands.append( message )
    return True


#call this in a main loop (or rewrite into separate Thread - would be nice)
def update_comms():
    global last_time, pending_commands

    if open_port():
        now = millis()
        if (now - last_time) >= forced_delay and len(pending_commands) > 0:
            #while len(pending_commands) > 0:
                send_now( pending_commands.pop(0) )
                #print (last_time, now)
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

def sendack():
    send_now( 'rf:a' + config.FIELD_ID + config.ROBOT_ID + 'ACK------') #PING and personal commands must be answered
    #time.sleep(.1)
    print("ACK sent\n")

# mainboard doesnt send much useful information
# set failsade, send ack where appropriate
def parse_incoming_message ( message ):
    #global config.BRAKES_ON
    global pending_commands

    #what referee has to say?
    if message.startswith('<ref:'):
        package = message[5:-1]
        print ( message )

        if package[0] == 'a' and (len(package) >= 12 or package[-1] == '-'): #seems legit
            fid, rid, com = package[1], package[2], package[3: package.find('-') ]
            if com not in ['PING','START','STOP']:
                print ('..garbage\n')
                return False

            #else recognizable command
            if fid == config.FIELD_ID and rid in [config.ROBOT_ID, 'X']:
                if com == 'PING' and rid == config.ROBOT_ID:
                    sendack()

                if com == 'START':
                    #maybe less ack is good thing?
                    if config.BRAKES_ON and rid == config.ROBOT_ID:
                        sendack()
                    config.BRAKES_ON = False
                    pending_commands = []
                    #send_now( 'st:40' )
                    #time.sleep(.1)
                    #send_now( 'r0' )
                    #time.sleep(.1)
                    print ("Houston, we have a liftoff!")

                elif com == 'STOP':
                    if not config.BRAKES_ON and rid == config.ROBOT_ID:
                        sendack()
                    config.BRAKES_ON = True
                    pending_commands = []
                    send_now( 'sm:0:0:0' )
                    time.sleep(.05)
                    send_now ( 'st:0' )
                    #time.sleep(.1)
                    #send_now ( 'r1' ) #red led on
                    #time.sleep(.1)
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
        _port = config.serialport
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


if config.BRAKES_ON:
    send_soon('r1')
else:
    send_soon('r0')


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
