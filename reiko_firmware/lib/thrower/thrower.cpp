#include "thrower.h"
#include "mbed.h"

/*
constructor-setup.
Internet suggests that driving servos and ESCs requires 20ms period (thats 50Hz?) and between 1-2ms pulsewidth. Only.
Also duty cycle and freuency is not critical, only pulsewidth is.
Does CortexM3 and mbed support different pwms frequencies? On AVR this was serious problem - you could set one speed for whole port, not individual pins.
Do not see any warnings, nor can i find clear guides. So lets just try it.

If it doesn't work (because setting period sets it for whole channel), then 1ms @ 50Hz should be doable with simple ticker.

Oooh, stupid. There are several highly optimised and reliable libraries also, surely.



TODO: speed feedback would be probably more useful for accurate throwing distance.
I still think that grabbing ball will not work - too little torque and too much
*/

Thrower::Thrower( DigitalOut *pwm, InterruptIn *ir/*, DigitalOut *led */) {

  _pwm = pwm;
  _ir  = ir;
  //_led = led;

  //_pwm->period_ms(20);
  //_pwm->write(0.5);
  //this->setSpeed(20);
  ESCTicker.attach_us(this, &Thrower::PulseRise, 20000); //20ms period


  //_pwm->write(0);
  for(int p=0; p<80; p += 10) {
       this->setSpeed(p);
       wait(0.5);
   }
   for(int p=80; p>0; p -= 10) {
        this->setSpeed(p);
        wait(0.5);
    }


  _ir->fall(callback(this, &Thrower::ballwatcher) );
  _ir->rise(callback(this, &Thrower::ballwatcher) );

}




//private:
/*
TODO: maybe we need some kind of ramp-up, but hopefully esc handles it. Perhaps can this esc be programmed too? By this program? Theoretically, yes. But its not very practical.
TODO: probably should program period_us and pulsewidth_us, instead of write.
*/

void Thrower::PulseRise() {
    _pwm->write(1);
    //_led->write(1);
    PulseTimeout.attach_us(this, &Thrower::PulseFall, _speed);
}
void Thrower::PulseFall() {
    _pwm->write(0);
    //_led->write(0);
}



void Thrower::setSpeed (int16_t speed){
  if (speed < 0) speed = 0;
  if (speed > 1000) speed = 1000;

  _speed = 1000 + speed; //local _speed is pulsewidth in us, 1000 - 2000. setSpeed takes percentage 0..100.
  // _pwm-> pulsewidth_us( 1000 + speed*10 ); //value needs to be between 1000 and 2000 (or so they say)
  // 
}


/*
Act on IR interrupt: set status, possibly count, possibly grab (shut off motor), indicate on led.
*/
void Thrower::ballwatcher(){
  if ( _ir->read() ) {
    has_ball = true;
    //_led->write(0);

  } else {
    has_ball = false;
    //_led->write(1);
  }


}
