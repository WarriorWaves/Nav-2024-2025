#include <Servo.h>

Servo clawServo;
Servo rollServo;

void setup() {
    Serial.begin(9600);
    clawServo.attach(9);  // Adjust pin
    rollServo.attach(10); // Adjust pin
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        int separatorIndex = command.indexOf(':');

        if (separatorIndex > 0) {
            String servo = command.substring(0, separatorIndex);
            int position = command.substring(separatorIndex + 1).toInt();

            if (servo == "claw") {
                clawServo.write(position);
            } else if (servo == "roll") {
                rollServo.write(position);
            }
        }
    }
}