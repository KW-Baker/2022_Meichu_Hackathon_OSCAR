#include <TM1637.h>
#include <ESP32Servo.h>

#define rxPin 10
#define txPin 11
#define LED_PIN 25

#define Servo_up 12
#define Servo_dw 13

#define NO   3
#define STOP 7

int CLK = 14;
int DIO = 27;

int acc = 1.5;

uint8_t data = 10;
TM1637 tm(CLK,DIO);

Servo myservo_up;
Servo myservo_dw;

int angle_up = 90;
int angle_dw = 90;

void setup() {
  
  Serial2.begin(115200); // board
  Serial.begin(115200); // PC
  
  // put your setup code here, to run once:
  tm.init();
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW); 
  //set brightness; 0-7
  tm.set(2);
  displayNumber(0000);

  myservo_up.attach(Servo_up);
  myservo_dw.attach(Servo_dw);
  
}


void displayNumber(int num){   
    tm.display(3, num % 10);   
    tm.display(2, num / 10 % 10);   
    tm.display(1, num / 100 % 10);   
    tm.display(0, num / 1000 % 10);
}


void loop() {
  // put your main code here, to run repeatedly:

  // example: "1234"
  //displayNumber(0001);
  if(Serial2.available() > 0){
      data = Serial2.read();
      Serial.print(data);
  }

  // servo
  myservo_up.write(angle_up);
  delay(50);
  
  myservo_dw.write(angle_dw);
  delay(50);



  
  switch(data){
    case 0: // down
      angle_up = 0;
      myservo_up.write(angle_up);
      delay(50);
      
      myservo_dw.write(angle_dw);
      delay(50);
      
      displayNumber(0);
      
      break;
      
    case 1: // go
      displayNumber(1);
      for(float i = angle_up; i <= 180; i = i+acc){
        angle_up = i;
        myservo_up.write(angle_up);
        delay(25);                
      }
      
      if(Serial2.available() > 0){
          data = Serial2.read();
          Serial.print(data);
      }

      if(data == STOP || data == NO){
        break;
      }

      for(float i = angle_dw; i <= 180; i = i+acc){
        angle_dw = i;
        myservo_dw.write(angle_dw);
        delay(25);
      }

      if(Serial2.available() > 0){
          data = Serial2.read();
          Serial.print(data);
      }

      if(data == STOP || data == NO){
        break;
      }
      //////////////////////////////////////////////////

      for(float i = 0; i <= 180; i = i+acc){
        angle_up = 180 - i;
        myservo_up.write(angle_up);
        delay(25);                
      }
      
      if(Serial2.available() > 0){
          data = Serial2.read();
          Serial.print(data);
      }

      if(data == STOP || data == NO){
        break;
      }

      for(float i = 0; i <= 180; i = i+acc){
        angle_dw = 180 - i;
        myservo_dw.write(angle_dw);
        delay(25);
      }

      if(Serial2.available() > 0){
          data = Serial2.read();
          Serial.print(data);
      }

      if(data == STOP || data == NO){
        break;
      }
      
      
      break;
      
    case 2: // left
      angle_dw = 0;

      myservo_up.write(angle_up);
      delay(50);
      
      myservo_dw.write(angle_dw);
      
      delay(50);
      displayNumber(2);
      break;
      
    case NO: // no
      angle_up = 90;
      angle_up = 90;
      myservo_up.write(angle_up);
      delay(50);
      
      myservo_dw.write(angle_dw);
      
      delay(50);
      
      displayNumber(3);
      break;
      
    case 4: // off
      displayNumber(4);
      digitalWrite(LED_PIN, LOW); 
      break;
      
    case 5: // on
      displayNumber(5);
      digitalWrite(LED_PIN, HIGH); 
      break;
      
    case 6: // right
      angle_dw = 180;

      myservo_up.write(angle_up);
      delay(50);
      
      myservo_dw.write(angle_dw);
      delay(50);
      
      displayNumber(6);
      break;
      
    case STOP: // stop
      displayNumber(7);
      break;

    case 8: // up
      displayNumber(8);
      
      angle_up = 180;
      myservo_up.write(angle_up);
      delay(50);
      
      myservo_dw.write(angle_dw);
      delay(50);
      
      break;

    case 9: // yes
      displayNumber(9);

      break;

    
    default:
      displayNumber(1111);
      break;
  }

//  myservo_up.write(angle_up);
//  delay(50);
//  
//  myservo_dw.write(angle_dw);
//  delay(50);

}
