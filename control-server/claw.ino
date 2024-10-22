#include <Servo.h>

Servo clawServo;
Servo rollServo;

const int CLAW_PIN = 9;  // Adjust if needed
const int ROLL_PIN = 10; // Adjust if needed

void setup() {
    Serial.begin(9600);
    while (!Serial) {
        ; // Wait for serial port to connect. Needed for native USB port only
    }
    
    if (clawServo.attach(CLAW_PIN) == 0) {
        Serial.println("Error attaching claw servo");
    }

    if (rollServo.attach(ROLL_PIN) == 0) {
        Serial.println("Error attaching roll servo");
    }
    
    Serial.println("Servo Control Ready");
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        command.trim(); // Remove any whitespace
        int separatorIndex = command.indexOf(':');
        
        if (separatorIndex != -1) {
            String servo = command.substring(0, separatorIndex);
            int position = command.substring(separatorIndex + 1).toInt();
            
            if (servo == "claw") {
                if (position >= 0 && position <= 180) {
                    clawServo.write(position);
                    Serial.println("Claw moved to position: " + String(position));
                } else {
                    Serial.println("Invalid claw position. Use 0-180.");
                }
            } else if (servo == "roll") {
                if (position >= 0 && position <= 180) {
                    rollServo.write(position);
                    Serial.println("Roll moved to position: " + String(position));
                } else {
                    Serial.println("Invalid roll position. Use 0-180.");
                }
            } else {
                Serial.println("Unknown servo: " + servo);
            }
        } else {
            Serial.println("Invalid command format. Use 'servo:position'");
        }
    }
}