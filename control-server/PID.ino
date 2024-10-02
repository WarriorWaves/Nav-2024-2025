#include <Servo.h>
#include "MS5837.h"
#include <PID_v1.h>
#include <Wire.h>

// PID control variables
double dKp = 500, dKi = 5, dKd = 1;
double depthInput, depthOutput;
double depthSetpoint = 0.5;

// Initialize PID with depth control variables
PID depthPID(&depthInput, &depthOutput, &depthSetpoint, dKp, dKi, dKd, DIRECT);

// Initialize servos
Servo top_front;
Servo top_back;

// Initialize depth sensor
MS5837 depthSensor;

void setup() {
  Wire.begin();
  Serial.begin(9600); // Initialize serial communication
  depthPID.SetOutputLimits(-200, 200); // Set PID output limits
  depthPID.SetMode(AUTOMATIC); // Set PID to automatic mode
  depthSensorSetup(); // Initialize depth sensor
  motorSetup(); // Initialize motors
  Serial.println("System ready"); // Indicate system is ready
}

long microseconds;

void loop() {
  readSerialInput(); // Read depth setpoint from serial
  updateDepth(); // Update depth readings and PID control
  applyThrust(); // Apply PID output to thrusters
  while (micros() - microseconds < 250) {
    delayMicroseconds(1);
  }
}

void readSerialInput() {
  if (Serial.available()) {// Check if serial data is available
    float incomingValue = Serial.parseFloat(); // Read incoming serial float value
    if (incomingValue != 0) {// If a valid float value is received
      depthSetpoint = incomingValue; // Set the new depth setpoint
    }
  }
}

void updateDepth(){
  depthSensor.read(); // Read depth sensor data
  depthInput = depthSensor.depth(); // Get current depth
  depthPID.Compute(); // Compute PID control

  // Send depth input and setpoint values to serial monitor
  Serial.print("DepthInput: ");
  Serial.print(depthInput);
  Serial.print(", Setpoint: ");
  Serial.println(depthSetpoint);
}

void applyThrust() {
  // Apply PID output to thrusters
  int thrustValue = static_cast<int>(depthOutput) + 1500;
  topBack.writeMicroseconds(thrustValue);
  topFront.writeMicroseconds(thrustValue);
}

void depthSensorSetup() {
  depthSensor.setModel(MS5837::MS5837_02BA); // Set sensor model
  depthSensor.init(); // Initialize the sensor
  depthSensor.setFluidDensity(997); // Set fluid density (997 for freshwater, 1029 for seawater)
}

void motorSetup() {
  top_front.attach(5); // Attach front thruster to pin 5
  top_back.attach(2);  // Attach back thruster to pin 2
  top_front.writeMicroseconds(1500); // Initialize front thruster to neutral (1500 microseconds)
  top_back.writeMicroseconds(1500);  // Initialize back thruster to neutral (1500 microseconds)
  delay(7000); // Delay to stabilize motor setup
}
