
#include "mbed.h"
//#include "mbed_events.h" //do we have mbed ver 3? Anyway, cannot get events to work.
#include "rtos.h"  //threads
//Note: NEVER believe simple examples from web. There are thousands library invariants out there.
//RTOS can be forced to work in web-compiler, but here it proves to be challenging.
// platformio.ini needed: build_flags = -DPIO_FRAMEWORK_MBED_RTOS_PRESENT
//- After adding library into lib Atom needs to be restarted.

//TODO: something takes few seconds to initialize at boot. usbserial?
// how does usbserial handle random disconnects?

//TODO: implement safety shutoff after loss of guidance? Eg shut off motors 5sec after last setspeed? Especially thrower.

#include "definitions.h"
#include "pins.h"
#include <motor.h>
#include <USBSerial.h>
#include <thrower.h>

//TODO: <> and "" here in includes do not seem right. But Atom doesn't care much, it seems.
//TODO: i have strong suspicion that motor.cpp can be used much more nicely. (here are lots of ancient artefacts)


//NB! Must be easily changeable - possibly should get from parentprogram over pc serial
//first char is field [AB], second char robot [ABCD]
//XX is broadcast to all.
char FIELD_ID = 'A';
char ROBOT_ID = 'Z';



typedef void (*VoidArray) ();

//thrower is implemented without changing PWM, therefore it should not
Thrower thrower( &THROW_PWM, &IR_SENSOR, &LEDB);

//USBSerial pc;
USBSerial pc (0x1f00, 0x2012, 0x0001,    false);
//This last one is for connect_blocking, which i currently do not like. Look at USBSerial.h.
//Theroretically, if unexpected disconnect happens, this should throw an exception in python,
//wich can be trapped and reconnected after a while.
const unsigned int SERIAL_BUFFER_SIZE = 30; //resized and repaired bug in previous bugfix which did'nt take it into account
char buf[SERIAL_BUFFER_SIZE];
bool serialData = false;
unsigned int serialCount = 0;
void serialInterrupt();
void parseCommand_loop();

//and all the same for xbee.... not nice. Really not nice.
Serial xb (P0_0, P0_1);
char xbuf[SERIAL_BUFFER_SIZE];
bool xserialData = false;
unsigned int xserialCount = 0;
void xbeeInterrupt();
void xbee_loop();


// why isn't ticking etc implemented in motor.cpp?
// Here i should have only 3 instances of motor and thats kinda it.
//TODO: I strongly feel that those are messed up.
//TODO: study maximum speed.

Ticker motorPidTicker[NUMBER_OF_MOTORS];
volatile int16_t motorTicks[NUMBER_OF_MOTORS];
volatile uint8_t motorEncNow[NUMBER_OF_MOTORS]; //encoder 0..255
volatile uint8_t motorEncLast[NUMBER_OF_MOTORS];

Motor motors[NUMBER_OF_MOTORS];

//here they are declared manually, and expanded with dragons from definitions.h
void motor0EncTick();
void motor1EncTick();
void motor2EncTick();

void motor0PidTick();
void motor1PidTick();
void motor2PidTick();




//Lets try to utilise somehow those huge discolights, i mean RGB-leds.
// I have a problem where green led flashes full power after reset.
//"After a reset all pins behave as DigitalInputs and have a pull-up to high level.
// When you declare a pin as DigitalOut it will go to low level until you change the state.
// This may result in an undesired short pulse with logic low level. There is a new feature
//in the mbed lib to define the state of a newly declared pin. (DigitalOut blabla(pin, 1))
//But no such thing for pwmout i'm afraid.
//somehow this initialization takes visibly long time, atleast 10ms. Oh well. Would'nt be a problem
//if leds be connected other way.


// Tried like 5 different variants. Only ticker+timeout worked.
// And yet another way: RTOS threading. Seems simple enough. Wont be picky IRS but somekind of queueing.
// .. which might be just perfect for diagnosing starve-out issues.

Thread hb_thread;
void heartbeat_loop() {
    while (1) {
      LED2G.write(0.5);
      Thread::wait(80); //allows to switch processes or sleep inbetween
      LED2G.write(0.98);
      Thread::wait(80);
      LED2G.write(0.5);
      Thread::wait(100);
      LED2G.write(0.98);
      Thread::wait(2000);
    }
}


//EventQueue queue;
//Ticker parseTicker; //oy, ticker is implemented by ISR, and this is allergic to blocking calls (pc.print)

Thread pc_thread;

/*
    PWMout.write takes float, wich represents percentage between 0..1.
    Leds are connected in active-low configuration, so
    0 means fully on,
    1 means fully off.
    Only LED2G has native pwm unfortunately.

    why led starts with full power in beginning? Because.. PWM defaults to active low, and there is no simple way around it.
    only that initialization should take no more than microsecond, but i see at least 10 ms delay.
*/

void warmup() {
  LEDB = 0; //reversed it was
  wait_ms(100);
  LEDB = 1;
}




int main() {
      warmup();

      // create a thread that'll keeps running the event queue's dispatch function
      //Thread eventThread;
      //eventThread.start(callback(&queue, &EventQueue::dispatch_forever));
      // events are simple callbacks. Since dispatch_forever seems to be a hanging loop, then there is no use of it.
      //queue.dispatch(1);
      //parseTicker.attach( &parseCommand, 0.1); //10ms

      pc.attach( &serialInterrupt ); //now serialintterupt is ticking its merry way and gathering data quietly
      xb.attach( &xbeeInterrupt );

      hb_thread.start( heartbeat_loop );

      //pc_thread.start( parseCommand_loop );

      //hb_thread.set_priority( osPriorityBelowNormal );
      //needs yielding (but not yield()) in main thread or it never fires.

       void (*encTicker[])()  = {
           motor0EncTick,
           motor1EncTick,
           motor2EncTick
       };

       VoidArray pidTicker[] = {
           motor0PidTick,
           motor1PidTick,
           motor2PidTick
       };

       //setup motors
       for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
           MotorEncA[i]->mode(PullNone);
           MotorEncB[i]->mode(PullNone);

           motors[i] = Motor(&pc, MotorPwm[i], MotorDir1[i], MotorDir2[i], MotorFault[i]);

           motorTicks[i] = 0;
           motorEncNow[i] = 0;
           motorEncLast[i] = 0;

           //encTicker is not ticker, but interrupt handler
           MotorEncA[i]->rise( encTicker[i] );
           MotorEncA[i]->fall( encTicker[i] );
           MotorEncB[i]->rise( encTicker[i] );
           MotorEncB[i]->fall( encTicker[i] );

           motorPidTicker[i].attach(pidTicker[i], 0.05); //0.1 seconds? Kinda slow?

           motors[i].init();
       }
/**/


       int count = 0;
       while(1) {
           if (count % 10000 == 0) {
               for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
                   pc.printf("s%d:%d\n", i, motors[i].getSpeed());
               }
           }

           parseCommand_loop();
           xbee_loop();
           wait_ms(1);
           count++;
       }
} //end of main()


//todo: should be in usbserial too. As i need two serials, therefore it gets very ugly very quickly
void serialInterrupt(){
   while(pc.readable()) {
       buf[serialCount] = pc.getc();
       serialCount++;
       serialData = false;

       if (serialCount >= SERIAL_BUFFER_SIZE) { //zeroes buffer and starts again. Therefore all commands must fit into SERIAL_BUFFER_SIZE or else...
           memset(buf, 0, SERIAL_BUFFER_SIZE);
           serialCount = 0;
       }
   }

   if (buf[serialCount - 1] == '\n') {
       serialData = true;
       serialCount = 0;
   }
}


//quick hack - just copypastarenamemodify
void xbeeInterrupt(){
   while( xb.readable() ) {
       xbuf[xserialCount] = xb.getc();
       xserialCount++;
       xserialData = false;

       if (xserialCount >= SERIAL_BUFFER_SIZE) { //zeroes buffer and starts again. Therefore all commands must fit into SERIAL_BUFFER_SIZE or else...
           memset(xbuf, 0, SERIAL_BUFFER_SIZE);
           xserialCount = 0;
       }
   }

   //command starts with 'a' and is 12 bytes long, padded with '-'. I believe, hope, that '-' does not occur before end.
   if (xbuf[0] == 'a' && (xbuf[xserialCount-1] == '-' || xserialCount == 13) ) {
       xserialData = true;
       xserialCount = 0;
       xbuf[xserialCount] = '\0';
   }
}




//TODO:
// + timing issue
// + thrower's speed.
// + single command for motors
// - leds.

//during connection some noise is injected into buffer and first command is often ignored?
//redone as a tighter loop in a separate thread - it is not strictly time-critical.
//Threading did'nt work. Probably because i do not understand sharing resources.
void parseCommand_loop () {

   if (!serialData) {
      return;
      //Thread::wait(5);
      //continue;
   }

   serialData = false;
   static char command[SERIAL_BUFFER_SIZE];
   memcpy(command, buf, SERIAL_BUFFER_SIZE);
   //buffer could still change during those few ticks? oh well.

   pc.printf("gotcommand: %s", command); //hangs on "g"???

   //a23|-2323|100 - set all motors' speed with one command
   if (command[0] == 'a') { //"a" stands for "All motors"
      int speed0, speed1, speed2;
      if (sscanf(command, "a%d|%d|%d%*s", &speed0, &speed1, &speed2) == 3) {
        //some sanity check.
        if (speed0 <= 1000 && speed0 >= -1000 &&
            speed1 <= 1000 && speed1 >= -1000 &&
            speed2 <= 1000 && speed2 >= -1000 )
           {
                motors[0].setSpeed(speed0);
                motors[1].setSpeed(speed1);
                motors[2].setSpeed(speed2);
           }
        pc.printf("gotspeeds %d %d %d\n", speed0, speed1, speed2);

      } else
        pc.printf("didnt get you..");

   //t255 - set thrower speed. "t" stands for "Thrower" of course.
   } else if (command[0] == 't') {
     int speed;
     if (sscanf(command, "t%d%*s", &speed) == 1)
        thrower.setSpeed( speed );

   //todo: led indication (a set of messages instead of direct control?), status reports...
   /**/
   //for debugging PID only
   } else if (command[0] == 'p' && command[1] == 'p') {
       uint8_t pGain = atoi(command + 2);
       motors[0].pgain = pGain;
   } else if (command[0] == 'p' && command[1] == 'i') {
       uint8_t iGain = atoi(command + 2);
       motors[0].igain = iGain;
   } else if (command[0] == 'p' && command[1] == 'd') {
       uint8_t dGain = atoi(command + 2);
       motors[0].dgain = dGain;
   } else if (command[0] == 'p') {
       char gain[20];
       motors[0].getPIDGain(gain);
       pc.printf("%s\n", gain);
   /**/
   } else //couldn't understand
     pc.printf("..ignored: %s\n", command);
//}
}

//Listen for referee commands over XBEE
//packet protocol: 12chars, filled with dash (-).
// START|2BYTE ID|9BYTE DATA.
//START STOP PING, send ACK

void xbee_loop(){
  if (!xserialData)
    return;

  xserialData = false;
  static char packet[SERIAL_BUFFER_SIZE];
  memcpy(packet, xbuf, SERIAL_BUFFER_SIZE);

  pc.printf("xbee reports: %s\n", packet);

  //try to act on command.
  if (packet[0]=='a' && packet[1] == FIELD_ID) { //meant for this field
     //oh, but what is the command?
     if ( strstr(packet, "PING") && packet[2] == ROBOT_ID ){  //ping this robot
        //TODO: consult with NUC, whether we really are ready?
        xb.printf("a%c%cACK------");
     } else
     if ( strstr(packet, "STOP") ){
        if (packet[2] == ROBOT_ID) xb.printf("a%c%cACK------", FIELD_ID, ROBOT_ID); //meant for us
        //TODO: EMERGENCY BRAKE!!!
        motors[0].referee_stop();
        motors[1].referee_stop();
        motors[2].referee_stop();
        thrower.setSpeed(0);
     } else
     if ( strstr(packet, "START") ){
        if (packet[2] == ROBOT_ID) xb.printf("a%c%cACK------", FIELD_ID, ROBOT_ID);
        motors[0].referee_start();
        motors[1].referee_start();
        motors[2].referee_start();
        thrower.setSpeed(20);
     }

  } else
      //TODO: comment out in action
      pc.printf("xbee ignored: %s\n", packet);
}



   //here be dragons (which i need to kill)
   //if i understand it correctly:
   //those are 3+3 functions
   // motor0..2EncTick which reads encoder and updates motorTicks
   // and motor0..2Pidtick which calls motor.pid2() and resets motorTicks.
   // EncTicker is called upon rise or fall interrupt,
   // pidticker is called by timer

   MOTOR_ENC_TICK(0)
   MOTOR_ENC_TICK(1)
   MOTOR_ENC_TICK(2)

   MOTOR_PID_TICK(0)
   MOTOR_PID_TICK(1)
   MOTOR_PID_TICK(2)
