//    Uno           WAV Trigger
//    ===           ===========
//    GND  <------> GND
//    Pin9 <------> RX

//    RPi           Uno
//    ===           ===
//    8             D2 = INTO
//    10            D3 = B0
//    12            D4 = B1
//    16            D5 = B2
//    18            D6 = B3
//    22            D7 = B4
//    24            D8 = B5

#include <Metro.h>
#include <AltSoftSerial.h>
#include <wavTrigger.h>

// 6 bits from RPi choose 1 of 64 tons
#define INTO 0
#define D2 2 // INTO
#define B0 3
#define B1 4
#define B2 5
#define B3 6
#define B4 7
#define B5 8

wavTrigger wTrig;
Metro gWTrigMetro = Metro(400);
int         i = 0;
byte RPiFlag  = 0;
bool bit0     = 0;
bool bit1     = 0;
bool bit2     = 0;
bool bit3     = 0;
bool bit4     = 0;
bool bit5     = 0;
int  ton      = 0;

void setup() 
{
  Serial.begin(9600);
  Serial.print("F_CPU = ");Serial.println(F_CPU);                                     
  Serial.println("InoFromRPi.160501b.ino");
  pinMode(B0,INPUT);
  pinMode(B1,INPUT);
  pinMode(B2,INPUT);
  pinMode(B3,INPUT);
  pinMode(B4,INPUT);
  pinMode(B5,INPUT);
  attachInterrupt(INT0,RPiInterrupt,FALLING);
  wTrig.start();
}

void RPiInterrupt()
{
  RPiFlag=1;
}

void loop() 
{
  if(RPiFlag==1)
  {
    bit0=0;
    bit1=0;
    bit2=0;
    bit3=0;
    bit4=0;
    bit5=0;
    bit0=digitalRead(B0);
    bit1=digitalRead(B1);
    bit2=digitalRead(B2);
    bit3=digitalRead(B3);
    bit4=digitalRead(B4);
    bit5=digitalRead(B5);
    Serial.print(bit5);
    Serial.print(bit4);
    Serial.print(bit3);
    Serial.print(bit2);
    Serial.print(bit1);
    Serial.println(bit0);
    ton=bit0+bit1*pow(2,1)+bit2*pow(2,2)+bit3*pow(2,3)+bit4*pow(2,4)+bit5*pow(2,5);
    Serial.println(ton);
    wTrig.trackPlayPoly(ton);
    RPiFlag=0;
  }
}
// This code successfully receives codes 0-63 from RPiToIno.160501a.py. 
// 470 ohm resistors connect RPi digital output pins to Uno digital input pins.
// It also successfully played 24 tons at .1 second intervals triggered from RPi.
