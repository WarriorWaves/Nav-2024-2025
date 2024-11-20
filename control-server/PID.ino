#include <Servo.h>
#include "MS5837.h"
#include <PID_v1.h>
#include <Wire.h>

double dKp = 500, dKi = 5, dKd = 1; // Change based off of calibration 
double depthInput, depthOutput;
double depthSetpoint = 0.5;  

PID depthPID(&depthInput, &depthOutput, &depthSetpoint, dKp, dKi, dKd, DIRECT);
Servo top_front;
Servo top_back;

MS5837 depthSensor;

double dKp_tune, dKi_tune, dKd_tune;

unsigned long lastTime = 0;
const unsigned long stabilizationPeriod = 100; //Change is too long or short 

const double MIN_DEPTH = 0.1;
const double MAX_DEPTH = 5.0;

bool depthSensorFailed = false;

void setup() {
  Wire.begin();
  Serial.begin(9600);  
  depthPID.SetOutputLimits(-200, 200); 
  depthPID.SetMode(AUTOMATIC); 
  depthSensorSetup(); 
  motorSetup(); 
  Serial.println("System ready"); 
}

long microseconds;

void loop() {
  readSerialInput(); 
  updateDepth(); 
  applyThrust(); 
  
  while (micros() - microseconds < stabilizationPeriod * 1000) {
    delayMicroseconds(1);
  }
}

void readSerialInput() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.startsWith("SET_DEPTH")) {
      float incomingValue = input.substring(9).toFloat();
      if (incomingValue >= MIN_DEPTH && incomingValue <= MAX_DEPTH) {
        depthSetpoint = incomingValue;
        Serial.print("Depth setpoint updated to: ");
        Serial.println(depthSetpoint);
      } else {
        Serial.println("Invalid depth setpoint. Must be between 0.1m and 5m.");
      }
    }
    else if (input.startsWith("TUNE_PID")) {
      sscanf(input.c_str(), "TUNE_PID %lf %lf %lf", &dKp_tune, &dKi_tune, &dKd_tune);
      depthPID.SetTunings(dKp_tune, dKi_tune, dKd_tune);
      Serial.print("PID Tunings updated - Kp: ");
      Serial.print(dKp_tune);
      Serial.print(", Ki: ");
      Serial.print(dKi_tune);
      Serial.print(", Kd: ");
      Serial.println(dKd_tune);
    }
  }
}

void updateDepth() {
  if (depthSensor.read()) {
    depthInput = depthSensor.depth(); 
  } else {
    depthSensorFailed = true;
    Serial.println("Depth sensor failure. Stopping motors for safety.");
    stopMotors();
    return;
  }

  depthPID.Compute();

  Serial.print("Depth Input: ");
  Serial.print(depthInput);
  Serial.print(", Setpoint: ");
  Serial.print(depthSetpoint);
  Serial.print(", PID Output: ");
  Serial.println(depthOutput);
}

void applyThrust() {
  if (depthSensorFailed) {
    return; 
  }

  int thrustValue = constrain(static_cast<int>(depthOutput) + 1500, 1000, 2000); //Change
  topFront.writeMicroseconds(thrustValue);
  topBack.writeMicroseconds(thrustValue);
}

void stopMotors() {
  top_front.writeMicroseconds(1500); 
  top_back.writeMicroseconds(1500); 
}

void depthSensorSetup() {
  depthSensor.setModel(MS5837::MS5837_02BA);
  if (!depthSensor.init()) {
    Serial.println("Failed to initialize depth sensor");
    depthSensorFailed = true;
    stopMotors(); 
  }
  depthSensor.setFluidDensity(1000); 
}

void motorSetup() {
  top_front.attach(5); // Attach front thruster to pin 5
  top_back.attach(2);  // Attach back thruster to pin 2
  top_front.writeMicroseconds(1500); // Initialize front thruster to neutral (1500 microseconds)
  top_back.writeMicroseconds(1500);  // Initialize back thruster to neutral (1500 microseconds)
  delay(7000); // Delay to stabilize motor setup
}

