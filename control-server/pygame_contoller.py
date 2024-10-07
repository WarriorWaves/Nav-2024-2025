import os
import sys
import time
import serial
import pygame
from pygame.locals import *
import power_comp

# Constants
SERIAL_PORT = '/dev/ttyUSB0'  # Arduino's serial port
BAUD_RATE = 9600
SEND_SERIAL = True
ROV_MAX_AMPS = 25
MAX_TROTTLE = 0.5
RUN_THRUSTER = True
SOCKETEVENT = pygame.event.custom_type()

CTRL_DEADZONES = [0.2] * 6  # Adjust
MAPPING = [
    {"name": "OFR", "color": "cyan", "index": 0, "posIndex": 1, "rightpad": 1},
    {"name": "IFR", "color": "purple", "index": 1, "posIndex": 2, "rightpad": 0},
    {"name": "IBR", "color": "red", "index": 2, "posIndex": 3, "rightpad": 1},
    {"name": "IBL", "color": "yellow", "index": 3, "posIndex": 4, "rightpad": 0},
    {"name": "OFL", "color": "gray", "index": 4, "posIndex": 5, "rightpad": 2},
    {"name": "OBR", "color": "pink", "index": 5, "posIndex": 6, "rightpad": 0},
]
MAPPING_DICT = {item["name"]: item["index"] for item in MAPPING}

# Environment variables for joystick functionality
os.environ.update({
    "SDL_VIDEO_ALLOW_SCREENSAVER": "1",
    "SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS": "1",
    "SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS": "1",
    "SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR": "0"
})

def map_num(num, out_min, out_max, in_min=-1, in_max=1):
    return round(out_min + (float(num - in_min) / float(in_max - in_min) * (out_max - out_min)))

def format_message(message):
    output = "c" if RUN_THRUSTER else "c," + ",".join("1500" for _ in message)
    return output + "," + ",".join(map(str, message))

class MainProgram:
    def __init__(self):
        pygame.init()
        self.curcam = 1
        self.runpid = False
        self.camval = [60, 70, 95]
        self.runJoy = True
        self.maxThrottle = MAX_TROTTLE
        self.curMessage = ""
        self.wrist = 0  # 0 is flat, 1 is vertical

        self.last_axes = [0.0] * 6
        self.last_buttons = [0] * 12

        self.init_joystick()
        self.init_thrusters()

    def init_joystick(self):
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            print("No joysticks detected. Please connect at least one joystick.")
            self.quit(1)

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.axis_count = self.joystick.get_numaxes()
        self.button_count = self.joystick.get_numbuttons()

    def init_thrusters(self):
        up_thrust = [item["index"] for item in MAPPING]
        self.curMessage = "t," + ",".join(map(str, up_thrust))
        print(self.curMessage)
        self.send_serial()

        self.curMessage = "p,550,9,1"
        print(self.curMessage)
        self.send_serial()

    def run(self):
        print("Running")
        while True:
            for event in pygame.event.get():
                self.handle_event(event)

            self.process_axes()
            if self.axes_changed():
                self.control()

    def handle_event(self, event):
        if event.type == QUIT:
            self.quit()
        elif event.type == JOYAXISMOTION:
            self.last_axes[event.axis] = event.value
        elif event.type in (JOYBUTTONUP, JOYBUTTONDOWN):
            self.last_buttons[event.button] = int(event.type == JOYBUTTONDOWN)
        elif event.type == SOCKETEVENT:
            self.handle_socket_event(event)

    def handle_socket_event(self, event):
        print("Socket event: " + str(event.message))
        if event.message == "STATUS":
            time.sleep(0.1)
        elif "PIDOFF" in event.message:
            self.runpid = False
            self.curMessage = "f"
            self.send_serial()
            self.control()
        elif "PIDON" in event.message:
            self.runpid = True
            self.curMessage = "n"
            self.send_serial()
            self.control()
        elif "Power:" in event.message:
            self.maxThrottle = float(event.message.split(":")[1])
            print("Power: " + str(self.maxThrottle))
        elif "c" in event.message:
            self.runJoy = False
            self.curMessage = event.message
            self.send_serial()
        elif "xy" in event.message:
            self.curMessage = event.message
            self.send_serial()
        elif event.message == "RUN":
            self.runJoy = True

    def process_axes(self):
        self.axes = [0.0 if abs(value) < CTRL_DEADZONES[i] else round(value, 2) 
                     for i, value in enumerate(self.last_axes)]

    def axes_changed(self):
        return str(self.axes) != str(self.last_axes) or str(self.buttons) != str(self.last_buttons)

    def control(self):
        if RUN_THRUSTER:
            if self.last_buttons[2]:  # Square button
                self.runpid = not self.runpid
                self.curMessage = "n" if self.runpid else "f"
                print("Running PID" if self.runpid else "Stopping PID")
                self.send_serial()

        # Throttle management
        self.maxThrottle = 0.3 if self.last_axes[-2] == 1 else 0.50 if self.last_axes[-2] == -1 else self.maxThrottle

        # Control logic
        sway = -self.axes[2]  # right stick left-right
        heave = self.axes[3]  # right stick up-down

        if self.last_buttons[0]:  # X button
            surge, yaw = 0, 0
            roll, pitch = -self.axes[0], self.axes[1]
        else:
            surge = self.axes[1]
            yaw = -self.axes[0]
            roll = pitch = 0

        combined_thrust = {
            "OFR": surge - yaw - sway,  # Front Right
            "IFR": heave + roll - pitch, # Inner Front Right
            "IBR": heave + roll + pitch, # Inner Back Right
            "IBL": heave - roll - pitch, # Inner Back Left
            "OFL": surge + yaw + sway,   # Front Left
            "OFR": surge - yaw + sway,   # Outer Back Right
        }

        combined = [0] * 6  # Adjusted for 6 thrusters
        for key, value in combined_thrust.items():
            combined[MAPPING_DICT[key]] = value

        # Normalize thrust values
        max_motor = max(abs(x) for x in combined) or 1  # Prevent division by zero
        max_input = max(abs(surge), abs(sway), abs(heave), abs(yaw), abs(pitch), abs(roll))

        for i in range(len(combined)):
            combined[i] = map_num(
                (combined[i] / max_motor * max_input),
                1500 - (400 * self.maxThrottle),
                1500 + (400 * self.maxThrottle),
            )

        combined = power_comp.calcnew(combined, ROV_MAX_AMPS)

        if self.last_buttons[1]:  # Circle button
            self.wrist = (self.wrist + 1) % 2  # Toggle wrist position

        self.curMessage = format_message(combined)
        self.send_serial()

    def send_serial(self):
        if SEND_SERIAL:
            try:
                print("Sending serial: " + self.curMessage)
                arduino.write((self.curMessage + '\n').encode('utf-8'))
            except Exception as e:
                print(f"Error sending data to Arduino: {e}")

    def quit(self, status=0):
        print("Exiting program...")
        pygame.quit()
        sys.exit(status)

if __name__ == "__main__":
    try:
        arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        program = MainProgram()
        program.run()
    except serial.SerialException as e:
        print(f"Could not open serial port {SERIAL_PORT}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
