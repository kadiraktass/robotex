#include "mbed.h"
#include "rtos.h"
//Note: NEVER believe simple examples from web. There are thousands library invariants out there.
//RTOS can be forced to work in web-compiler, but here it proves to be challenging.
// platformio.ini needed: build_flags = -DPIO_FRAMEWORK_MBED_RTOS_PRESENT
//- After adding library into lib Atom needs to be restarted.

#include "definitions.h"
#include "pins.h"
#include <motor.h>
#include <USBSerial.h>
#include <thrower.h>

//TODO: <> and "" here in includes do not seem right. But Atom doesn't care much, it seems.

/*
I detect some kind of anomaly - programmer does not want to work, but works after pulling USB serial, and resetting mainboard...
automount fails kindof often too.
And programming seems kinda slow. And fails.
*/


typedef void (*VoidArray) ();

Thrower thrower( &THROW_PWM, &IR_SENSOR, &LEDB);

//USBSerial pc;
USBSerial pc (0x1f00, 0x2012, 0x0001,    false);
//This last one is for connect_blocking, which i currently do not like. Look at USBSerial.h.
//Theroretically, if unexpected disconnect happens, this should throw an exception in python, wich can be trapped and reconnected after a while.


const unsigned int SERIAL_BUFFER_SIZE = 16;

char buf[SERIAL_BUFFER_SIZE];
bool serialData = false;
unsigned int serialCount = 0;
void serialInterrupt();
void parseCommand(char *command);


// why isn't ticking etc implemented in motor.cpp?
// Here i should have only 3 instances of motor and thats kinda it.

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
      Thread::wait(80);
      LED2G.write(0.98);
      Thread::wait(80);
      LED2G.write(0.5);
      Thread::wait(100);
      LED2G.write(0.98);
      Thread::wait(2000);
    }
}



/* I think that for debugging it might be useful to visually detect unexpected
    reboot - therefore this unneeded intro wasting ~2 seconds.
    PWMout.write takes float, wich represents percentage between 0..1.
    Leds are connected in active-low configuration, so
    0 means fully on,
    1 means fully off.
    Only LED2G has native pwm unfortunately.

    why led starts with full power in beginning? Because.. PWM defaults to active low, and there is no simple way around it.
    only that initialization should take no more than microsecond, but i see at least 10 ms delay.
*/

void warmup() {
    for (int i=20; i<100; i++) {
      LED2G.write((float) i / 100);
      wait_ms(30);
    }
    for (int i=100; i>50; i--) {
      LED2G.write((float) i / 100);
      wait_ms(30);
    }
    wait_ms(300);
}




int main() {

      warmup();
      pc.attach( &serialInterrupt ); //now serialintterupt is ticking its merry way and gathering data quietly
      pc.printf("Ready? Start your engines!\n");

      hb_thread.start( heartbeat_loop );
      bt_thread.start( bluetooth_loop );

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


/*
       motors[0].setSpeed(100);
       motors[1].setSpeed(100);
       motors[2].setSpeed(100);
*/
       int count = 0;
       while(1) {
           if (count % 20 == 0) {
               for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
                   pc.printf("s%d:%d\n", i, motors[i].getSpeed());
               }
           }

           if (serialData) {
               char temp[16];
               memcpy(temp, buf, 16);
               memset(buf, 0, 16);
               serialData = false;
               parseCommand(temp);
           }

           wait_ms(20);
           count++;
       }
} //end of main()


void serialInterrupt(){
   while(pc.readable()) {
       buf[serialCount] = pc.getc();
       serialCount++;
       if (serialCount >= SERIAL_BUFFER_SIZE) {
           memset(buf, 0, SERIAL_BUFFER_SIZE);
           serialCount = 0;
       }
   }
   if (buf[serialCount - 1] == '\n') {
       serialData = true;
       serialCount = 0;
   }
}



//TODO: redo.
void parseCommand (char *command) {

   pc.printf("gotsmthng");
/*
   char *searcha = command;
   char *a;
   int indexa;
   a=strchr(searcha, 'a');
   indexa = int(a - searcha);

   char *searchb = command;
   char *b;
   int indexb;
   b=strchr(searchb, 'b');
   indexb = int(b - searchb);


   char *searchc = command;
   char *c;
   int indexc;
   c=strchr(searchc, 'c');
   indexc = int(c - searchc);




   char *searchd = command;
   char *d;
   int indexd;
   d=strchr(searchd, 'd');
   indexd = int(d - searchd);

   int16_t speeda = atoi(command + (indexa+1));
   motors[0].pid_on = 1;
   motors[0].setSpeed(speeda);

   int16_t speedb = atoi(command + (indexb+1));
   motors[1].pid_on = 1;
   motors[1].setSpeed(speedb);

   int16_t speedc = atoi(command + (indexc+1));
   motors[2].pid_on = 1;
   motors[2].setSpeed(speedc);

   if (command[0] == 's' && command[1] == 'd' && command[2] == '0') {
       int16_t speed = atoi(command + 3);
       motors[0].pid_on = 1;
       motors[0].setSpeed(speed);
   }
   if (command[0] == 's' && command[1] == 'd' && command[2] == '1') {
       int16_t speed = atoi(command + 3);
       motors[1].pid_on = 1;
       motors[1].setSpeed(speed);
   }
   if (command[0] == 's' && command[1] == 'd' && command[2] == '2') {
       int16_t speed = atoi(command + 3);
       motors[2].pid_on = 1;
       motors[2].setSpeed(speed);
   }
   if (command[0] == 'f') {
       int16_t speed = atoi(command + 1);
       motors[0].pid_on = 1;
       motors[0].setSpeed(-speed);
       motors[2].pid_on = 1;
       motors[2].setSpeed(speed);
   }
   if (command[0] == 'b' && command[1] == '1' && command[2] == '2') {
       int16_t speed = atoi(command + 3);
       motors[1].pid_on = 1;
       motors[1].setSpeed(speed);
       motors[2].pid_on = 1;
       motors[2].setSpeed(speed);
   }

   if (command[0] == 'b' && command[1] == '0' && command[2] == '1') {
       int16_t speed = atoi(command + 3);
       motors[0].pid_on = 1;
       motors[0].setSpeed(speed);
       motors[1].pid_on = 1;
       motors[1].setSpeed(speed);
    }
   if (command[0] == 'b' && command[1] == '0' && command[2] == '2') {
       int16_t speed = atoi(command + 3);
       motors[0].pid_on = 1;
       motors[0].setSpeed(speed);
       motors[2].pid_on = 1;
       motors[2].setSpeed(speed);
     }
   if (command[0] == 'a') {
       int16_t speed = atoi(command + 1);
       motors[0].pid_on = 1;
       motors[0].setSpeed(speed);
       motors[1].pid_on = 1;
       motors[1].setSpeed(speed);
       motors[2].pid_on = 1;
       motors[2].setSpeed(speed);
   }


   if (command[0] == 's') {
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

  uint8_t spd = 0;
  LEDG = 1;


  while (true) {

        if (bluetoothSerial.readable()) {
           bluetoothCommand = bluetoothSerial.getc();
           pc.printf( "%c", bluetoothCommand );
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
            motors[0].setSpeed(spd);
            motors[2].setSpeed(-spd);
        }
        if(bluetoothCommand == 'B') {  //BACK
          motors[0].setSpeed(-spd);
          motors[2].setSpeed(spd);
        }

        if(bluetoothCommand == 'S') {  //STOP
          motors[0].setSpeed(0);
          motors[1].setSpeed(0);
          motors[2].setSpeed(0);
        }

        //turn in spot.
        //todo:crab-motion? But this reuires some maths...
        if(bluetoothCommand == 'L') {  //LEFT
          motors[0].setSpeed(30);
          motors[1].setSpeed(30);
          motors[2].setSpeed(30);
        }

        if(bluetoothCommand == 'R') {  //RIGHT
          motors[0].setSpeed(-30);
          motors[1].setSpeed(-30);
          motors[2].setSpeed(-30);
        }


        //SET MOTORS SPEED
        if(bluetoothCommand == '0') {
          spd = 10;
        }
        if(bluetoothCommand == '1') {
          spd = 30;
        }
        if(bluetoothCommand == '2') {
          spd = 50;
        }
        if(bluetoothCommand == '3') {
          spd = 70;
        }
        if(bluetoothCommand == '4') {
          spd = 90;
        }
        if(bluetoothCommand == '5') {
          spd = 110;
        }
        if(bluetoothCommand == '6') {
          spd = 130;
        }
        if(bluetoothCommand == '7') {
          spd = 150;
        }
        if(bluetoothCommand == '8') {
          spd = 170;
        }
        if(bluetoothCommand == '9') {
          spd = 200;
        }
    /**/

        lastCommand = bluetoothCommand;
  }
}



   //here be dragons
   MOTOR_ENC_TICK(0)
   MOTOR_ENC_TICK(1)
   MOTOR_ENC_TICK(2)

   MOTOR_PID_TICK(0)
   MOTOR_PID_TICK(1)
   MOTOR_PID_TICK(2)
