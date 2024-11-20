#include <Wire.h>

const int imuAddress = 0x68;  // MPU-6050 I2C address
int accelX, accelY, accelZ, gyroX, gyroY, gyroZ;

void setup() {
  Serial.begin(9600);  
  Wire.begin();
  Wire.beginTransmission(imuAddress);
  Wire.write(0x6B);  
  Wire.write(0);    
  Wire.endTransmission(true);
}

void loop() {
  Wire.beginTransmission(imuAddress);
  Wire.write(0x3B);  
  Wire.endTransmission(false);
  Wire.requestFrom(imuAddress, 14, true);

  accelX = (Wire.read() << 8) | Wire.read();
  accelY = (Wire.read() << 8) | Wire.read();
  accelZ = (Wire.read() << 8) | Wire.read();
  gyroX = (Wire.read() << 8) | Wire.read();
  gyroY = (Wire.read() << 8) | Wire.read();
  gyroZ = (Wire.read() << 8) | Wire.read();

  Serial.print("Accel X: "); Serial.print(accelX); Serial.print(" ");
  Serial.print("Y: "); Serial.print(accelY); Serial.print(" ");
  Serial.print("Z: "); Serial.print(accelZ); Serial.print(" | ");
  Serial.print("Gyro X: "); Serial.print(gyroX); Serial.print(" ");
  Serial.print("Y: "); Serial.print(gyroY); Serial.print(" ");
  Serial.print("Z: "); Serial.println(gyroZ);

  delay(100);  
}
