#include <Servo.h>

// Servo definitions
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
  Serial.begin(9600);  // Start serial communication at 9600 baud

  // Attach servos to their respective pins
  t1.attach(6);
  t2.attach(8);
  t3.attach(10);
  t4.attach(12);
  t5.attach(2);
  t6.attach(4);
  s1.attach(9);
  s2.attach(5);
  s3.attach(7);

  // Initialize servos to neutral positions
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
  // Check if data is available on the serial port
  if (Serial.available() > 0){
    // Read the incoming serial data
    String msg = Serial.readStringUntil('\n');  // Read until newline character
    Serial.println("Received: " + msg);

    char command = msg[0];  // First character is the command
    String data = msg.substring(2);  // Rest of the message is the data
    sendData = data;  // Prepare the data to send back (if necessary)

    if (command == 'c'){
      // Convert the received data string into an array of integers for servo control
      int output[11];
      boolean done = false;
      int i = 0;
      while (!done){
        int index = data.indexOf(',');
        if (index == -1){
          done = true;
          output[i] = data.toInt();  // Convert the last part to an integer
        } else {
          output[i] = data.substring(0, index).toInt();  // Convert the substring to an integer
          data = data.substring(index + 1);  // Remove the parsed part from the string
          i++;
        }
      }

      // Write the received values to the respective thrusters and servos
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
