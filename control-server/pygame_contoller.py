import sys
import time
import subprocess
import os
import pygame
from pygame.locals import *
import power_comp
import serial

# Initialize serial communication
SERIAL_PORT = '/dev/ttyUSB0'  # Update this with your Arduino's serial port
BAUD_RATE = 9600
arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

SEND_SERIAL = True
ROV_MAX_AMPS = 25
MAX_TROTTLE = 0.5
RUN_THRUSTER = True
SOCKETEVENT = pygame.event.custom_type()

mapping = [
    {"name": "OFL", "color": "gray", "index": 2, "posIndex": 0, "rightpad": 2},
    {"name": "OFR", "color": "cyan", "index": 0, "posIndex": 1, "rightpad": 1},
    {"name": "IFL", "color": "blue", "index": 1, "posIndex": 2, "rightpad": 0},
    {"name": "IFR", "color": "purple", "index": 5, "posIndex": 3, "rightpad": 2},
    {"name": "IBL", "color": "yellow", "index": 3, "posIndex": 4, "rightpad": 0},
    {"name": "IBR", "color": "red", "index": 4, "posIndex": 5, "rightpad": 1},
    {"name": "OBL", "color": "orange", "index": 7, "posIndex": 6, "rightpad": 2},
    {"name": "OBR", "color": "pink", "index": 6, "posIndex": 7, "rightpad": 0},
]
mapping_dict = {item["name"]: item["index"] for item in mapping}
print(mapping_dict)

# Get the device IP (this part might not be needed for serial communication)
command = "ifconfig | grep 192 |awk '/inet/ {print $2; exit}' "
result = subprocess.run(
    command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
)
device_ip = ""
if result.returncode == 0:
    device_ip = result.stdout.strip()
else:
    print(f"Command failed with error: {result.stderr}")

# Environment variables to make joystick work in the background
os.environ["SDL_VIDEO_ALLOW_SCREENSAVER"] = "1"
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
os.environ["SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
os.environ["SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR"] = "0"

CTRL_DEADZONES = [0.2] * 6  # Adjust these to your liking.

def mapnum(num, outMin, outMax, inMin=-1, inMax=1):
    return round(outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin)))

def formatMessage(message):
    output = "c"
    if RUN_THRUSTER:
        for i in range(len(message)):
            output += "," + str(message[i])
    else:
        for i in range(len(message)):
            output += ",1500"
    return output

class mainProgram(object):
    def __init__(self):
        pygame.init()
        self.curcam = 1
        self.runpid = False
        self.camval = [60, 70, 95]
        self.runJoy = True
        self.maxThrottle = MAX_TROTTLE
        self.curMessage = ""
        self.wrist = 0  # 0 is flat, 1 is vertical

        self.lastaxes = []
        self.lastbuttons = []

        pygame.joystick.init()
        self.joycount = pygame.joystick.get_count()
        if self.joycount == 0:
            print("This program only works with at least one joystick plugged in. No joysticks were detected.")
            self.quit(1)
        
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.axiscount = self.joystick.get_numaxes()
        self.buttoncount = self.joystick.get_numbuttons()
        self.axes = [0.0] * self.axiscount
        self.buttons = [0] * self.buttoncount

        # Initialize thrust controls
        upthrust = [item["index"] for item in mapping if "I" in item["name"]]
        self.curMessage = "t," + ",".join(str(x) for x in upthrust)
        print(self.curMessage)
        self.sendSerial()

        self.curMessage = "p,550,9,1"
        print(self.curMessage)
        self.sendSerial()

    def run(self):
        print("Running")
        pygameRunning = True
        while pygameRunning:
            for event in [pygame.event.wait()] + pygame.event.get():
                if event.type == QUIT:
                    pygameRunning = False
                elif event.type == JOYAXISMOTION:
                    self.axes[event.axis] = event.value
                elif event.type == JOYBUTTONUP:
                    self.buttons[event.button] = 0
                elif event.type == JOYBUTTONDOWN:
                    self.buttons[event.button] = 1
                elif event.type == SOCKETEVENT:
                    print("Socket event: " + str(event.message))
                    if event.message == "STATUS":
                        time.sleep(0.1)
                    if "PIDOFF" in event.message:
                        self.runpid = False
                        self.curMessage = "f"
                        self.sendSerial()
                        self.control()
                    if "PIDON" in event.message:
                        self.runpid = True
                        self.curMessage = "n"
                        self.sendSerial()
                        self.control()
                    if "Power:" in event.message:
                        self.maxThrottle = float(event.message.split(":")[1])
                        print("Power: " + str(self.maxThrottle))
                    if "c" in event.message:
                        self.runJoy = False
                        self.curMessage = event.message
                        self.sendSerial()
                    if "xy" in event.message:
                        self.curMessage = event.message
                        self.sendSerial()
                    if event.message == "RUN":
                        self.runJoy = True

            for i in range(len(self.axes)):
                if abs(self.axes[i]) < CTRL_DEADZONES[i]:
                    self.axes[i] = 0.0
                self.axes[i] = round(self.axes[i], 2)

            if str(self.axes) != str(self.lastaxes) or str(self.buttons) != str(self.lastbuttons):
                self.lastaxes = list(self.axes)
                self.lastbuttons = list(self.buttons)
                if self.runJoy:
                    self.control()

    def control(self):
        if RUN_THRUSTER:
            if self.buttons[2] == 1:  # square button
                self.runpid = not self.runpid
                if self.runpid:
                    self.curMessage = "n"
                    print("Running PID")
                else:
                    self.curMessage = "f"
                    print("Stopping PID")
                self.sendSerial()

        if self.axes[-2] == 1 and not self.maxThrottle == 0.3:  # left trigger is index: 5
            self.maxThrottle = 0.3
        elif self.axes[-2] == -1 and not self.maxThrottle == 0.50:
            self.maxThrottle = 0.50

        sway = -self.axes[2]  # right stick left-right
        heave = self.axes[3]  # right stick up-down

        if self.buttons[0] == 0:  # x button
            surge = self.axes[1]
            yaw = -self.axes[0]
            roll = 0
            pitch = 0
        else:
            surge = 0
            yaw = 0
            roll = -self.axes[0]
            pitch = self.axes[1]

        combinedthrust = {
            "IFL": heave - roll + pitch,
            "OFR": surge - yaw - sway,
            "OFL": surge + yaw + sway,
            "IBL": heave - roll - pitch,
            "IBR": heave + roll - pitch,
            "IFR": heave + roll + pitch,
            "OBR": surge - yaw + sway,
            "OBL": surge + yaw - sway,
        }

        combined = [0] * 8
        for key, value in combinedthrust.items():
            combined[mapping_dict[key]] = value

        max_motor = max(abs(x) for x in combined)
        max_input = max(abs(surge), abs(sway), abs(heave), abs(yaw), abs(pitch), abs(roll))
        if max_motor == 0:
            max_motor = 1

        for i, t in enumerate(combined):
            combined[i] = mapnum(
                (t / max_motor * max_input),
                1500 - (400 * self.maxThrottle),
                1500 + (400 * self.maxThrottle),
            )

        combined = power_comp.calcnew(combined, ROV_MAX_AMPS)

        if self.buttons[1] == 1:  # circle button
            self.wrist += 1
            if self.wrist > 1:
                self.wrist = 0

        self.curMessage = formatMessage(combined)
        self.sendSerial()

    def sendSerial(self):
        if SEND_SERIAL:
            try:
                print("Sending serial: " + self.curMessage)
                arduino.write(self.curMessage.encode('utf-8') + b'\n')
            except Exception as e:
                print(f"Error sending data to Arduino: {e}")

    def quit(self, code=0):
        pygame.quit()
        if SEND_SERIAL:
            arduino.close()
        sys.exit(code)

if __name__ == "__main__":
    app = mainProgram()
    app.run()
