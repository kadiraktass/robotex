#ifndef PINS_H_
#define PINS_H_
#include "mbed.h"
#include "definitions.h"
/*
yuk,  "multiple definition of..." error kicks in.
Problem is in defining pins as they are here. Now every .cpp which includes pins.h, gets its own copy resulting in confused linker.
https://stackoverflow.com/questions/223771/repeated-multiple-definition-errors-from-including-same-header-in-multiple-cpps
I could do it properly, by NOT using pins.h in leds.cpp (by object references),
I could stuff everything into massive file,
or i could hack it... Hmm... No luck, suggested trick with externs plainly did not work.
*/


//Brushless motor. No way to change direction. Well, with a additional relay actually could...
PwmOut THROW_PWM(P2_4);

//Infrared ball sensor. High level means blocked path. Sensor already has some hysteresis, lets hope it's enough.
InterruptIn IR_SENSOR(P2_11);


// LEDS the way I use them.
// LED2 is used only for green hearbeat indication.
PwmOut LED2G(P1_18);


// LED1 must provide all status reports.
DigitalOut LEDR(P4_28, 1);
DigitalOut LEDG(P4_29, 1);
DigitalOut LEDB(P2_8, 1);

//Motors A, B, C (or 0, 1, 2)
PwmOut MOTOR0_PWM(P2_3);
DigitalOut MOTOR0_DIR1(P0_21);
DigitalOut MOTOR0_DIR2(P0_20);
DigitalIn MOTOR0_FAULT(P0_22);
InterruptIn MOTOR0_ENCA(P0_19);
InterruptIn MOTOR0_ENCB(P0_18);

PwmOut MOTOR1_PWM(P2_2);
DigitalOut MOTOR1_DIR1(P0_15);
DigitalOut MOTOR1_DIR2(P0_16);
DigitalIn MOTOR1_FAULT(P0_17);
InterruptIn MOTOR1_ENCA(P2_7);
InterruptIn MOTOR1_ENCB(P2_6);


PwmOut MOTOR2_PWM(P2_1);
DigitalOut MOTOR2_DIR1(P0_24);
DigitalOut MOTOR2_DIR2(P0_25);
DigitalIn MOTOR2_FAULT(P0_23);
InterruptIn MOTOR2_ENCA(P0_26);
InterruptIn MOTOR2_ENCB(P0_9);

/* will not use
PwmOut MOTOR3_PWM(P2_0);
DigitalOut MOTOR3_DIR1(P0_7);
DigitalOut MOTOR3_DIR2(P0_6);
DigitalIn MOTOR3_FAULT(P0_8);
InterruptIn MOTOR3_ENCA(P0_5);
InterruptIn MOTOR3_ENCB(P0_4);
*/

PwmOut* MotorPwm[] = {
    &MOTOR0_PWM,
    &MOTOR1_PWM,
    &MOTOR2_PWM
};

DigitalOut* MotorDir1[] = {
    &MOTOR0_DIR1,
    &MOTOR1_DIR1,
    &MOTOR2_DIR1
};

DigitalOut* MotorDir2[] = {
    &MOTOR0_DIR2,
    &MOTOR1_DIR2,
    &MOTOR2_DIR2
};

DigitalIn* MotorFault[] = {
    &MOTOR0_FAULT,
    &MOTOR1_FAULT,
    &MOTOR2_FAULT
};

InterruptIn* MotorEncA[] = {
    &MOTOR0_ENCA,
    &MOTOR1_ENCA,
    &MOTOR2_ENCA
};

InterruptIn* MotorEncB[] = {
    &MOTOR0_ENCB,
    &MOTOR1_ENCB,
    &MOTOR2_ENCB
};

#endif
