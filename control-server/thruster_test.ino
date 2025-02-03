#include <Servo.h>

byte thrusterPin = 6;  
Servo thruster;

void setup() {
    Serial.begin(9600);  
    thruster.attach(thrusterPin);

    Serial.println("Sending initial stop signal");
    thruster.writeMicroseconds(1500);  

    Serial.println("Waiting for ESC to initialize...");
    delay(7000); 
    Serial.println("ESC should be initialized now");
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        int pwmValue = command.toInt();
        if (pwmValue >= 1100 && pwmValue <= 1900) {
            thruster.writeMicroseconds(pwmValue);
            Serial.print("Applied PWM: ");
            Serial.println(pwmValue);
        } else {
            thruster.writeMicroseconds(1500);
            Serial.println("Invalid PWM value - setting to neutral");
        }
    }
    
    delay(10);
}