import os
import sys
import time
import serial

print("Current Working Directory:", os.getcwd())

# Constants
SERIAL_PORT = '/dev/ttyUSB0'  # Arduino's serial port
BAUD_RATE = 9600
SEND_SERIAL = True
ROV_MAX_AMPS = 25
MAX_TROTTLE = 0.5
RUN_THRUSTER = True

#fix
MAPPING = [
    {"name": "OFR", "color": "cyan", "index": 0, "posIndex": 1, "rightpad": 1},
    {"name": "IFR", "color": "purple", "index": 1, "posIndex": 2, "rightpad": 0},
    {"name": "IBR", "color": "red", "index": 2, "posIndex": 3, "rightpad": 1},
    {"name": "IBL", "color": "yellow", "index": 3, "posIndex": 4, "rightpad": 0},
    {"name": "OFL", "color": "gray", "index": 4, "posIndex": 5, "rightpad": 2},
    {"name": "OBR", "color": "pink", "index": 5, "posIndex": 6, "rightpad": 0},
]

MAPPING_DICT = {item["name"]: item["index"] for item in MAPPING}

# Function to format the message for serial communication
def format_message(message):
    if RUN_THRUSTER:
        output = "c"
    else:
        output = "c," + ",".join("1500" for _ in message)  # Default throttle if not running
    return output + "," + ",".join(map(str, message))

class MainProgram:
    def __init__(self):
        self.maxThrottle = MAX_TROTTLE
        self.curMessage = ""
        self.init_thrusters()

    def init_thrusters(self):
        up_thrust = [item["index"] for item in MAPPING]
        self.curMessage = "t," + ",".join(map(str, up_thrust))
        print(self.curMessage)
        self.send_serial()

        # Example PWM value for T100 thrusters (you can adjust based on your requirements)
        self.curMessage = "p,550,9,1"  # Adjust as necessary
        print(self.curMessage)
        self.send_serial()

    def run(self):
        print("Running")
        while True:
            self.control()

    def control(self):
        # Example inputs that replace joystick inputs
        surge = float(input("Enter surge value (-1 to 1): "))
        sway = float(input("Enter sway value (-1 to 1): "))
        heave = float(input("Enter heave value (-1 to 1): "))
        yaw = float(input("Enter yaw value (-1 to 1): "))
        roll = float(input("Enter roll value (-1 to 1): "))
        pitch = float(input("Enter pitch value (-1 to 1): "))

        combined_thrust = {
            "OFR": surge - yaw - sway,  # Front Right
            "IFR": heave + roll - pitch, # Inner Front Right
            "IBR": heave + roll + pitch, # Inner Back Right
            "IBL": heave - roll - pitch, # Inner Back Left
            "OFL": surge + yaw + sway,   # Front Left
            "OBR": surge - yaw + sway,   # Outer Back Right
        }

        combined = [0] * 6  # Adjusted for 6 thrusters
        for key, value in combined_thrust.items():
            combined[MAPPING_DICT[key]] = value

        # Normalize thrust values to be between 1500 and 1650
        for i in range(len(combined)):
            # Map thrust values directly to PWM range for T100
            combined[i] = int(1500 + (combined[i] * 75))  # 75 is the scale factor to get max 1650

            # Clamp the values between 1500 and 1650
            combined[i] = min(max(combined[i], 1500), 1650)

        self.curMessage = format_message(combined)
        self.send_serial()
    # breaks in serial through intial stop 
    def send_serial(self):
        if SEND_SERIAL:
            try:
                print("Sending serial: " + self.curMessage)
                arduino.write((self.curMessage + '\n').encode('utf-8'))
            except Exception as e:
                print(f"Error sending data to Arduino: {e}")

if __name__ == "__main__":
    try:
        arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        program = MainProgram()
        program.run()
    except serial.SerialException as e:
        print(f"Could not open serial port {SERIAL_PORT}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
