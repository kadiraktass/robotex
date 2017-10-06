#include "thrower.h"
#include "mbed.h"

/*
constructor-setup.
*/
Thrower::Thrower( PwmOut *pwm, InterruptIn *ir, DigitalOut *led ) {
  _pwm = pwm;
  _ir  = ir;
  _led = led;

  setSpeed(10);

  _ir->fall(callback(this, &Thrower::ballwatcher) );
  _ir->rise(callback(this, &Thrower::ballwatcher) );

}




//private:
/*
Todo: maybe we need some kind of ramp-up, but hopefully esc handles it. Perhaps can this esc be programmed too?
*/
void Thrower::setSpeed (int16_t speed){
  if (speed < 0) speed = 0;
  if (speed > 100) speed = 100;

  _pwm->write( speed/100 );
}


/*
set status, possibly count, possibly grab (shut off motor), indicate on led.
*/
void Thrower::ballwatcher(){
  if ( _ir->read() ) {
    has_ball = true;
    _led->write(0);

  } else {
    has_ball = false;
    _led->write(1);
  }



}
