import serial
import pygame

SERIAL_PORT = '/dev/ttyUSB0'  
BAUD_RATE = 9600              
SEND_SERIAL = True            

# Thruster mapping 
MAPPING = [
    {"name": "FR", "index": 0},  # Front Right
    {"name": "FL", "index": 1},  # Front Left
    {"name": "BR", "index": 2},  # Back Right
    {"name": "BL", "index": 3},  # Back Left
    {"name": "F", "index": 4},   # Front (y-axis)
    {"name": "B", "index": 5},   # Back (y-axis)
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

        # Initialize thrust values
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
                "FR": surge - yaw - sway,  # Front Right
                "FL": surge + yaw + sway,  # Front Left
                "BR": surge - yaw + sway,  # Back Right
                "BL": surge + yaw - sway,  # Back Left
                "F": heave,  # Front (y-axis)
                "B": heave,  # Back (y-axis)
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
