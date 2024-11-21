#include <Servo.h>

Servo t1;
Servo t2;
Servo t3;
Servo t4;
Servo t5;
Servo t6;
Servo s1;
Servo s2;
Servo s3;
String sendData = "";

void setup()
{
  Serial.begin(9600);  

  t1.attach(6);
  t2.attach(8);
  t3.attach(10);
  t4.attach(12);
  t5.attach(2);
  t6.attach(4);
  s1.attach(9);
  s2.attach(5);
  s3.attach(7);

  t1.writeMicroseconds(1500);
  t2.writeMicroseconds(1500);
  t3.writeMicroseconds(1500);
  t4.writeMicroseconds(1500);
  t5.writeMicroseconds(1500);
  t6.writeMicroseconds(1500);
  s1.write(180);
  s2.write(159);
  s3.write(17);
}

void loop()
{
  if (Serial.available() > 0){
    String msg = Serial.readStringUntil('\n');  
    Serial.println("Received: " + msg);

    char command = msg[0]; 
    String data = msg.substring(2);  
    sendData = data;  

    if (command == 'c'){
      int output[11];
      boolean done = false;
      int i = 0;
      while (!done){
        int index = data.indexOf(',');
        if (index == -1){
          done = true;
          output[i] = data.toInt();  
        } else {
          output[i] = data.substring(0, index).toInt();  
          data = data.substring(index + 1);  
          i++;
        }
      }

      t1.writeMicroseconds(output[0]);
      t2.writeMicroseconds(output[1]);
      t3.writeMicroseconds(output[2]);
      t4.writeMicroseconds(output[3]);
      t5.writeMicroseconds(output[4]);
      t6.writeMicroseconds(output[5]);
      t7.writeMicroseconds(output[6]);
      t8.writeMicroseconds(output[7]);
      s1.write(output[8]);
      s2.write(output[9]);
      s3.write(output[10]);
    }
  }
  delay(100);
}
