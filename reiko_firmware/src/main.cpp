#include "mbed.h"
#include "pins.h"
#include "motor.h"
#include "RGBLed.hpp"
#include "USBSerial.h"
#include "RFManager.h"
#include "thrower.h"

bool failSafeEnabled = true;
int ticksSinceCommand = 0;

USBSerial serial;

Serial pc(USBTX, USBRX); //dud, only for motor??
RFManager rfModule(COMTX, COMRX);

char* ref;
//NB! Must be easily changeable - possibly should get from parentprogram over pc serial
//first char is field [AB], second char robot [ABCD]
//XX is broadcast to all.
//char FIELD_ID = 'A';
//char ROBOT_ID = 'Z';

RGBLed led1(LED1R, LED1G, LED1B);
RGBLed led2(LED2R, LED2G, LED2B);

Timeout kicker;

static const int NUMBER_OF_MOTORS = 3;

Motor motor0(&pc, M0_PWM, M0_DIR1, M0_DIR2, M0_FAULT, M0_ENCA, M0_ENCB);
Motor motor1(&pc, M1_PWM, M1_DIR1, M1_DIR2, M1_FAULT, M1_ENCA, M1_ENCB);
Motor motor2(&pc, M2_PWM, M2_DIR1, M2_DIR2, M2_FAULT, M2_ENCA, M2_ENCB);

Motor * motors[NUMBER_OF_MOTORS] = {
  &motor0, &motor1, &motor2
};

DigitalIn infrared(ADC0);

PwmOut m0(M0_PWM);
PwmOut m1(M1_PWM);
PwmOut m2(M2_PWM);

PwmOut pwm0(PWM0);
//PwmOut pwm1(PWM1);
DigitalOut THROW_PWM(P2_4);
InterruptIn IR_SENSOR(P2_11);

Thrower thrower( &THROW_PWM, &IR_SENSOR );


void serialInterrupt(); //notused
void parseCommand(char *command);

Ticker pidTicker;
int pidTickerCount = 0;
static const float PID_FREQ = 60;

char buf[100] = {0};
int serialCount = 0;
bool serialData = false;


void pidTick() {
  for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
    motors[i]->pidTick();
  }

  if (pidTickerCount++ % 25 == 0) {
    led1.setBlue(!led1.getBlue());
  }

  // Fail-safe
  if (failSafeEnabled) {
    ticksSinceCommand++;
  }
  //i upped it to 600
  if (ticksSinceCommand == 600) {
    for (int i = 0; i < NUMBER_OF_MOTORS; ++i) {
      motors[i]->setSpeed(0);
      //pwm1.pulsewidth_us(1000);
      thrower.setSpeed(0);
      //serial.printf("failsafe shutdown\n"); printf hangs here after "f"??!?! Something or other with ISRs?
    }


  }
}


int main() {
  pidTicker.attach(pidTick, 1/PID_FREQ);
  //serial.attach(&serialInterrupt);

  // Ball detector status
  int infraredStatus = -1;

  // Dribbler motor
  //pwm1.period_us(20000); //was 400 and 100
  //pwm1.pulsewidth_us(1050); // 1000 - 2000  (1-2ms)



  while (1) {

    if ( rfModule.readable() ) {
        //ref = rfModule.read();
        serial.printf("<ref:%s>\n", rfModule.read());
        //referee_command( ref );
    }
    rfModule.update(); //looks if there is something

    if (serial.readable()) {
      buf[serialCount] = serial.getc();

      if (buf[serialCount] == '\n') {
        parseCommand(buf);

        serialCount = 0;
        memset(buf, 0, 100);
      } else {

        serialCount++;
        if (serialCount >= 99) serialCount = 0; //possible overflow fix
      }
    }

    /// INFRARED DETECTOR
    int newInfraredStatus = infrared.read();
    if (newInfraredStatus != infraredStatus) {
      infraredStatus = newInfraredStatus;
      serial.printf("<ball:%d>\n", newInfraredStatus);
      led2.setGreen(infraredStatus);
    }

  }
}

//mainboard still hangs somewhere. All communication stops.
//why?
void parseCommand(char *buffer) {
  ticksSinceCommand = 0;
  //serial.printf("ack comm: %s\n", buffer);

  char *cmd = strtok(buffer, ":");

  // buffer == "sm:14:16:10:30"
  if (strncmp(cmd, "sm", 2) == 0) {
    for (int i = 0; i < NUMBER_OF_MOTORS; ++i) {
      motors[i] -> setSpeed( (int16_t) atoi(strtok(NULL, ":")) );
    }

    /*serial.printf("<gs:%d:%d:%d>\n",
      motors[0]->getSpeed(),
      motors[1]->getSpeed(),
      motors[2]->getSpeed()
    );
    */
  }

  //  st:1000 - 2000  - thrower speed.
  else if (strncmp(cmd, "st", 2) == 0) {
    /*if (command[1] == '0') {
      pwm1.pulsewidth_us(100);
    } else if (command[1] == '1') {
      pwm1.pulsewidth_us(268);
    } else*/ {
      //pwm1.pulsewidth_us(atoi(buffer + 2));
      //serial.printf("THROW\n");
      thrower.setSpeed( atoi(buffer+3) );

    }
    //pwm1.pulsewidth_us((int) atoi(command+1));
    //serial.printf("sending %d\n", (int) atoi(command+1));
  }

  else if (strncmp(cmd, "rf", 2) == 0) {
       rfModule.send(buffer + 3);
  }

  else if (strncmp(cmd, "gb", 2) == 0) {
    serial.printf("<ball:%d>\n", infrared.read());
  }

  else if (strncmp(cmd, "fs", 1) == 0) {
    failSafeEnabled = buffer[3] != '0';
  }


  else if (strncmp(cmd, "r", 1) == 0) {
    //led1.setRed( !led1.getRed() );
    led1.setRed( atoi(cmd + 1) );
  }

  else if (strncmp(cmd, "g", 1) == 0) {
    led1.setGreen(!led1.getGreen());
  }

  else if (strncmp(cmd, "b", 1) == 0) {
    led1.setBlue(!led1.getBlue());
  }
}
