#ifndef  THROWER_H
#define  THROWER_H
#include "mbed.h"

/*
Trying to encapsulate functioning of basketball throwing mechanism, which
consists of brushless outrunner motor and IR sensor.

*/

class Thrower {
public:
  Thrower( PwmOut *pwm, InterruptIn *ir, DigitalOut *led );

  bool has_ball;                  //changed by interrupt


  void setSpeed (int16_t speed);  //Speed of thrower, 0..100 percent.



private:
//    static const uint PWM_PERIOD_US = 1000;
    PwmOut *_pwm;
    InterruptIn *_ir;
    DigitalOut *_led;

    void ballwatcher(); //aka interrupt handler, sets has_ball
};
#endif
