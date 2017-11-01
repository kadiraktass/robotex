#include "mbed.h"
#include "pins.h"
#include "motor.h"
#include "RGBLed.hpp"
#include "USBSerial.h"
#include "RFManager.h"

bool failSafeEnabled = true;
int ticksSinceCommand = 0;

USBSerial serial;

Serial pc(USBTX, USBRX); //dud, only for motor??
RFManager rfModule(COMTX, COMRX);

char* ref;
//NB! Must be easily changeable - possibly should get from parentprogram over pc serial
//first char is field [AB], second char robot [ABCD]
//XX is broadcast to all.
char FIELD_ID = 'A';
char ROBOT_ID = 'Z';

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
PwmOut pwm1(PWM1);


void serialInterrupt();
void parseCommand(char *command);

Ticker pidTicker;
int pidTickerCount = 0;
static const float PID_FREQ = 60;

char buf[32];
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

  if (ticksSinceCommand == 60) {
    for (int i = 0; i < NUMBER_OF_MOTORS; ++i) {
      motors[i]->setSpeed(0);
    }

    pwm1.pulsewidth_us(100);
  }
}



void referee_command ( char * packet ){
  /*
  char* ack[12];
  ack = sprintf("a%c%cACK------", FIELD_ID, ROBOT_ID);

  if (packet[0]=='a' && packet[1] == FIELD_ID) { //meant for this field
   //oh, but what is the command?
   if ( strstr(packet, "PING") && packet[2] == ROBOT_ID ){  //ping this robot
      //TODO: consult with NUC, whether we really are ready?
      rfModule.send( &ack, 12 );
   } else
   if ( strstr(packet, "STOP") ){
     if (packet[2] == ROBOT_ID) rfModule.send( &ack, 12);
      //TODO: EMERGENCY BRAKE!!!
      //thrower.setSpeed(0);
   } else
   if ( strstr(packet, "START") ){
      if (packet[2] == ROBOT_ID) rfModule.send( &ack, 12 );
      //thrower.setSpeed(20);
   }

} else
    //TODO: comment out in action
    serial.printf("xbee ignored: %s\n", packet);
*/
}


int main() {
  pidTicker.attach(pidTick, 1/PID_FREQ);
  //serial.attach(&serialInterrupt);

  // Ball detector status
  int infraredStatus = -1;

  // Dribbler motor
  pwm1.period_us(400);
  pwm1.pulsewidth_us(100);



  while (1) {

    if ( rfModule.readable() ) {
        //ref = rfModule.read();
        serial.printf("<ref:%s>\n", rfModule.read());
        //referee_command( ref );
    }
    rfModule.update(); //looks if there is something
    //why i dont get anything?

    if (serial.readable()) {
      buf[serialCount] = serial.getc();
      if (buf[serialCount] == '\n') {
        serial.printf("got %s<", buf);

        parseCommand(buf);
        serialCount = 0;
        memset(buf, 0, 32);
      } else {
        serialCount++;
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



void parseCommand(char *buffer) {
  ticksSinceCommand = 0;

  char *cmd = strtok(buffer, ":");

  // buffer == "sd:14:16:10:30"
  if (strncmp(cmd, "sd", 2) == 0) {
    for (int i = 0; i < NUMBER_OF_MOTORS; ++i) {
      motors[i] -> setSpeed( (int16_t) atoi(strtok(NULL, ":")) );
    }

    serial.printf("<gs:%d:%d:%d>\n",
      motors[0]->getSpeed(),
      motors[1]->getSpeed(),
      motors[2]->getSpeed()
    );
  }

  if (strncmp(cmd, "d", 1) == 0) {
    /*if (command[1] == '0') {
      pwm1.pulsewidth_us(100);
    } else if (command[1] == '1') {
      pwm1.pulsewidth_us(268);
    } else*/ {
      pwm1.pulsewidth_us(atoi(buffer + 2));
    }
    //pwm1.pulsewidth_us((int) atoi(command+1));
    //serial.printf("sending %d\n", (int) atoi(command+1));
  }

  if (strncmp(cmd, "gs", 2) == 0) {
    serial.printf("<gs:%d:%d:%d>\n", motors[0]->getSpeed(), motors[1]->getSpeed(), motors[2]->getSpeed() );
  }

  if (strncmp(cmd, "rf", 2) == 0) {
       rfModule.send(buffer + 3);
  }

  if (strncmp(cmd, "r", 1) == 0) {
    led1.setRed(!led1.getRed());
  }

  if (strncmp(cmd, "g", 1) == 0) {
    led1.setGreen(!led1.getGreen());
  }

  if (strncmp(cmd, "b", 1) == 0) {
    led1.setBlue(!led1.getBlue());
  }

  if (strncmp(cmd, "gb", 2) == 0) {
    serial.printf("<ball:%d>\n", infrared.read());
  }

  if (strncmp(cmd, "fs", 1) == 0) {
    failSafeEnabled = buffer[3] != '0';
  }
}