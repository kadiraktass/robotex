
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
volatile bool serialData = false;
unsigned int serialCount = 0;
void serialInterrupt();
void parseCommand_loop();


// why isn't ticking etc implemented in motor.cpp?
// Here i should have only 3 instances of motor and thats kinda it.
//TODO: I strongly feel that those are messed up.
//TODO: study maximum speed.

Ticker motorPidTicker[NUMBER_OF_MOTORS];
volatile int16_t motorTicks[NUMBER_OF_MOTORS];
volatile uint8_t motorEncNow[NUMBER_OF_MOTORS];
volatile uint8_t motorEncLast[NUMBER_OF_MOTORS];

Motor motors[NUMBER_OF_MOTORS];

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
Thread bt_thread;
void bluetooth_loop();

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
      pc.printf("Ready? Start your engines!\n");

      hb_thread.start( heartbeat_loop );
      bt_thread.start( bluetooth_loop );
      pc_thread.start( parseCommand_loop );


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

       for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
           MotorEncA[i]->mode(PullNone);
           MotorEncB[i]->mode(PullNone);

           motors[i] = Motor(&pc, MotorPwm[i], MotorDir1[i], MotorDir2[i], MotorFault[i]);

           motorTicks[i] = 0;
           motorEncNow[i] = 0;
           motorEncLast[i] = 0;

           MotorEncA[i]->rise(encTicker[i]);
           MotorEncA[i]->fall(encTicker[i]);
           MotorEncB[i]->rise(encTicker[i]);
           MotorEncB[i]->fall(encTicker[i]);

           motorPidTicker[i].attach(pidTicker[i], 0.1);

           motors[i].init();
       }
/**/


       int count = 0;
       while(1) {
           if (count % 100 == 0) {
               for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
                   pc.printf("s%d:%d\n", i, motors[i].getSpeed());
               }
           }

           wait_ms(20);
           count++;
       }
} //end of main()



//https://os.mbed.com/blog/entry/Simplify-your-code-with-mbed-events/
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



//TODO:
// + timing issue
// + thrower's speed.
// - leds.
// + single command for motors

//during connection some noise is injected into buffer and first command is often ignored?
//redone as a tighter loop in a separate thread - it is not strictly time-critical.
void parseCommand_loop () {
while(1)  {

   if (!serialData) {
      Thread::wait(5);
      continue;
   }

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

   } else //couldn't understand
       pc.printf("..ignored: %s\n", command);

   /*
   if (command[0] == 's') { //get speed
       for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
           pc.printf("s%d:%d\n", i, motors[i].getSpeed());
       }
   } else if (command[0] == 'w' && command[1] == 'l') {
       int16_t speed = atoi(command + 2);
       motors[0].pid_on = 0;
       if (speed < 0) motors[0].backward(-1*speed/255.0);
       else motors[0].forward(speed/255.0);
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
   }
   */
}
}

//later will be removed.
//temporarily try to steer robot by bluetooth - just to show off.
//put it into Thread, and should be just fine.
void bluetooth_loop(){

  //Bluetooth module TX pin only
  //COM socket - Gnd, Vcc, Tx, Rx
  Serial bluetoothSerial(P0_0, P0_1);
  bluetoothSerial.baud(38400); //OBDII pin 1234

  char lastCommand;
  char bluetoothCommand;

  int spd = 0;
  LEDG.write(1);


  while (true) {

        if (bluetoothSerial.readable()) {
           bluetoothCommand = bluetoothSerial.getc();
           pc.printf( "BT:%c", bluetoothCommand );
        }

        if (bluetoothCommand == lastCommand)
            continue;
        //else...

        if (bluetoothCommand == 'X') {
          pc.printf( "EXIT" );
          LEDG = 0;
          return;
        }

        //i expect motors to be connected clockwise, 0, 1, 2., where 1 is at six.
        if(bluetoothCommand == 'F') {  //FORWARD
            motors[0].setSpeed(-spd);
            motors[2].setSpeed(spd);
        }
        if(bluetoothCommand == 'B') {  //BACK
          motors[0].setSpeed(spd);
          motors[2].setSpeed(-spd);
        }

        if(bluetoothCommand == 'S') {  //STOP
          motors[0].setSpeed(0);
          motors[1].setSpeed(0);
          motors[2].setSpeed(0);
        }

        //turn in spot.
        //todo:crab-motion? But this requires some maths...
        if(bluetoothCommand == 'L') {  //LEFT
          motors[0].setSpeed(-50);
          motors[1].setSpeed(-100);
          motors[2].setSpeed(-150);
        }

        if(bluetoothCommand == 'R') {  //RIGHT
          motors[0].setSpeed(100);
          motors[1].setSpeed(100);
          motors[2].setSpeed(100);
        }


        //SET MOTORS SPEED
        if(bluetoothCommand == '0') {
          spd = 20;
          thrower.setSpeed(0);
        }
        if(bluetoothCommand == '1') {
          spd = 50;
          thrower.setSpeed(20);
        }
        if(bluetoothCommand == '2') {
          spd = 80;
          thrower.setSpeed(30);
        }
        if(bluetoothCommand == '3') {
          spd = 100;
          thrower.setSpeed(40);
        }
        if(bluetoothCommand == '4') {
          spd = 120;
          thrower.setSpeed(50);
        }
        if(bluetoothCommand == '5') {
          spd = 150;
          thrower.setSpeed(60);
        }
        if(bluetoothCommand == '6') {
          spd = 200;
          thrower.setSpeed(70);
        }
        if(bluetoothCommand == '7') {
          spd = 300;
          thrower.setSpeed(80);
        }
        if(bluetoothCommand == '8') {
          spd = 400;
          thrower.setSpeed(90);
        }
        if(bluetoothCommand == '9') {
          spd = 500;
          thrower.setSpeed(100);
        }
    /**/

        lastCommand = bluetoothCommand;
  }
}



   //here be dragons (which i need to kill)
   MOTOR_ENC_TICK(0)
   MOTOR_ENC_TICK(1)
   MOTOR_ENC_TICK(2)

   MOTOR_PID_TICK(0)
   MOTOR_PID_TICK(1)
   MOTOR_PID_TICK(2)
