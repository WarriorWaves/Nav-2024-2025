#include <Wire.h>
#include <Servo.h>
#include <PID_v1.h>
#include "MS5837.h"
#include "TSYS01.h"

typedef struct dataStorage {
  int upThrusters[4];
    float p;
    float i;
    float d;
    int servoAngles[3];
    bool initialized;
} dataStorage;
dataStorage datastore;

Servo thrusters[6];
const byte thrusterPins[] = {6, 8, 10, 12, 2, 4};
const byte servoPins[] = {9, 5, 7};
Servo servos[3];

String sendData = "";
bool runpid = false;
bool minirunpid = false;
MS5837 depthSensor;
TSYS01 tempSensor;
double depthInput, depthOutput;
double depthSetpoint = -1;
PID depthPID(&depthInput, &depthOutput, &depthSetpoint, datastore.p, datastore.i, datastore.d, DIRECT);

int writedepth;

void setup() {
  
  Wire.begin();
  sensorSetup();
  Serial.begin(9600);

  datastore.upThrusters[0] = 0;
  datastore.upThrusters[1] = 5;
  datastore.upThrusters[2] = 4;
  datastore.upThrusters[3] = 3;
  datastore.p = 550;
  datastore.i = 5;
  datastore.d = 1;
  datastore.servoAngles[0] = 142;
  datastore.servoAngles[1] = 15;
  datastore.servoAngles[2] = 17;
  datastore.initialized = true; 

  
  for (int i = 0; i < 8; i++) {
        thrusters[i].attach(thrusterPins[i]);
        thrusters[i].writeMicroseconds(1500);
  }
    
  for (int i = 0; i < 3; i++) {
        servos[i].attach(servoPins[i]);
        servos[i].write(datastore.servoAngles[i]);
  }
  
  Serial.println(datastore.upThrusters[0]);
  Serial.println(datastore.servoAngles[0]);
  Serial.println(datastore.p);

  depthPID.SetOutputLimits(-200, 200);
  depthPID.SetMode(AUTOMATIC);
  depthPID.SetTunings(datastore.p, datastore.i, datastore.d);
  
}

const long interval = 100;
unsigned long previousMillis = 0;

void loop(){
  if (Serial.avaliable > 0){
    String msg = Serial.readStringUntil('\n');
    char command = msg[0];
    String data = msg.substring(2);

    depthSensor.read();
    tempSensor.read();
    depthInput = depthSensor.depth();

    if(command == 'c') {
      int output[11];
      boolean done = false;
      int i = 0;
      while(!done){
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
      //write to thrusters
      for (int i = 0; i < 6; i++) {
        thrusters[i].writeMicroseconds(output[i]);
      }
      minirunpid = false;
      for (int i = 0; i < 4; i++) {
        if (output[datastore.upThrusters[i]] != 1500) {
            depthSetpoint = depthInput;
            break;
        };
        if (i == 3) {
            minirunpid = true;
            Serial.println("STARTING MINI PID");
        }
      }

      for (int i = 0; i < 3; i++) {
        servos[i].write(output[i + 8]);
      }
    } else if (command = 'z') {
      datastore.p = data.substring(0, data.indexOf(',')).toFloat();
      datastore.i = data.substring(data.indexOf(',') + 1, data.lastIndexOf(',')).toFloat();
      datastore.d = data.substring(data.lastIndexOf(',') + 1, data.indexOf('d')).toFloat();
      depthSetpoint = data.substring(data.indexOf('d') + 1).toFloat();
      runpid = true;
      depthPID.SetMode(AUTOMATIC);
      depthPID.SetTunings(datastore.p, datastore.i, datastore.d);

       Serial.print(datastore.p);
       Serial.print(",");
       Serial.print(datastore.i);
       Serial.print(",");
       Serial.print(datastore.d);
       Serial.print(",");
    } else if (command = 'p') {
      datastore.p = data.substring(0, data.indexOf(',')).toFloat();
      datastore.i = data.substring(data.indexOf(',') + 1, data.lastIndexOf(',')).toFloat();
      datastore.d = data.substring(data.lastIndexOf(',') + 1).toFloat();
      depthPID.SetTunings(datastore.p, datastore.i, datastore.d);
    } else if (command = 'd') {
      depthSetpoint = data.toFloat();
    } else if (command == 's') {
      runpid = false;
      depthPID.SetMode(MANUAL);
      
      for (int i = 0; i < 6; i++) {
          thrusters[i].attach(thrusterPins[i]);
          thrusters[i].writeMicroseconds(1500);
      }
      
      for (int i = 0; i < 3; i++) {
          servos[i].attach(servoPins[i]);
          servos[i].write(datastore.servoAngles[i]);
      }
    } else if (command == 'n') {
      runpid = true;
      depthPID.SetMode(AUTOMATIC);
      Serial.println("STARTING PID");
    } else if (command == 'f') {
      runpid = false;
      depthPID.SetMode(MANUAL);

      Serial.println("STOPPING PID");
      sendData = "PIDOFF" + sendData;
    } else if (command = 't') {
      for (int i = 0; i < 4; i++) {
        datastore.upThrusters[i] = data.substring(i * 2, i * 2 + 1).toInt();
      }
    }
    free(msg);
    
  }

  if (millis() - previousMillis >= interval) {
    previousMillis = millis();
    if (runpid && minirunpid)
    {
      depthSensor.read();
      tempSensor.read();
      depthInput = depthSensor.depth();
      depthPID.Compute();
      writeDepth = int(trunc((depthOutput * -1) + 1500));
      sendData = "Setpoint: " + String(depthSetpoint) + " pwmwriting: " + String(writeDepth) + " depth: " + String(depthInput) + " temp: " + String(tempSensor.temperature());
      Serial.println(sendData);

      thrusters[datastore.upThrusters[0]].writeMicroseconds(writeDepth);
      thrusters[datastore.upThrusters[1]].writeMicroseconds(writeDepth);
      thrusters[datastore.upThrusters[2]].writeMicroseconds(writeDepth);
      thrusters[datastore.upThrusters[3]].writeMicroseconds(writeDepth);
    }
  }
}

void sensorSetup() {
  depthSensor.setModel(MS5837::MS5837_02BA);
  depthSensor.init();
  depthSensor.setFluidDensity(997); // kg/m^3 (997 freshwater, 1029 for seawater)
  tempSensor.init();
}
