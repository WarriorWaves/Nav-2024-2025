# pygame_controller.py
# This file handles all joystick input and Arduino communication

import serial
import pygame

# Constants for configuration
SERIAL_PORT = '/dev/ttyUSB0'  # Arduino USB port
BAUD_RATE = 9600               # Serial communication speed
SEND_SERIAL = True              # Enable/disable serial communication

# Thruster mapping configuration
MAPPING = [
    {"name": "OFR", "index": 0},  # Outer Front Right
    {"name": "IFR", "index": 1},  # Inner Front Right
    {"name": "IBR", "index": 2},  # Inner Back Right
    {"name": "IBL", "index": 3},  # Inner Back Left
    {"name": "OFL", "index": 4},  # Outer Front Left
    {"name": "OBR", "index": 5},  # Outer Back Right
]
MAPPING_DICT = {item["name"]: item["index"] for item in MAPPING}


class ROVController:
    def __init__(self):
        # Initialize pygame and joystick
        pygame.init()
        pygame.joystick.init()

        # Set up joystick
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            print("No joystick detected!")

        # Set up Arduino communication
        try:
            self.arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        except serial.SerialException as e:
            print(f"Could not open serial port {SERIAL_PORT}: {e}")
            self.arduino = None

        # Initialize thrust values (1500 is neutral position)
        self.current_thrust_values = [1500] * 6

    def send_serial(self, message):
        """Send commands to Arduino through serial port"""
        if self.arduino and SEND_SERIAL:
            try:
                print(f"Sending serial: {message}")
                self.arduino.write((message + '\n').encode('utf-8'))
            except Exception as e:
                print(f"Error sending data to Arduino: {e}")

    def process_joystick(self):
        """Process joystick input and convert to thruster commands"""
        pygame.event.pump()  # Process pygame events

        if self.joystick:
            # Read all joystick axes
            surge = self.joystick.get_axis(1)  # Forward/Backward
            sway = self.joystick.get_axis(0)   # Left/Right
            heave = self.joystick.get_axis(2)  # Up/Down
            yaw = self.joystick.get_axis(3)    # Rotation

            # Calculate combined thrust for each motor
            combined_thrust = {
                "OFR": surge - yaw - sway,     # Outer Front Right
                "IFR": heave,                  # Inner Front Right
                "IBR": heave,                  # Inner Back Right
                "IBL": heave,                  # Inner Back Left
                "OFL": surge + sway,           # Outer Front Left
                "OBR": surge - sway,           # Outer Back Right
            }

            # Convert thrust values to PWM signals (1500 ± 150)
            combined = [0] * 6
            for key, value in combined_thrust.items():
                idx = MAPPING_DICT[key]
                combined[idx] = int(1500 + (value * 75))  # Scale to PWM range
                combined[idx] = min(max(combined[idx], 1500), 1650)  # Limit range

            # Update current values and send to Arduino
            self.current_thrust_values = combined
            self.send_serial(f"c,{','.join(map(str, combined))}")

    def close(self):
        """Clean up resources"""
        if self.arduino:
            self.arduino.close()
        pygame.quit()

    def get_thrust_values(self):
        """Get the current thrust values"""
        return self.current_thrust_values
