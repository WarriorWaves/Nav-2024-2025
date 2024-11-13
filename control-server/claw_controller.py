import os
import sys
import serial
import pygame
from pygame.locals import *

# Constants
SERIAL_PORT = '/dev/cu.usbmodem21101'  # Arduino's serial port (corrected)
BAUD_RATE = 9600
SEND_SERIAL = True

# Servo positions
CLAW_CLOSED = 90   # Middle position
CLAW_OPEN = 180    # Fully open (flat sideways)
ROLL_MIN = 0
ROLL_MAX = 180

# Trigger indices (may need adjustment based on your specific controller)
LEFT_TRIGGER = 4
RIGHT_TRIGGER = 5

# Trigger threshold (adjust if needed)
TRIGGER_THRESHOLD = 0.1

# Environment variables for controller functionality
os.environ.update({
    "SDL_VIDEO_ALLOW_SCREENSAVER": "1",
    "SDL_TRIGGER_ALLOW_BACKGROUND_EVENTS": "1",
    "SDL_HINT_TRIGGER_ALLOW_BACKGROUND_EVENTS": "1",
    "SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR": "0"
})

class MainProgram:
    def __init__(self):
        pygame.init()
        self.arduino = None  # Initialize arduino as None
        self.controller = None  # Initialize controller as None
        self.init_controller()  # Initialize the controller first
        self.init_serial()  # Initialize serial connection here
        self.claw_position = CLAW_CLOSED
        self.roll_position = 90  # Start at middle position

    def init_controller(self):
        pygame.joystick.init()
        while pygame.joystick.get_count() == 0:
            print("No controllers detected. Please connect a PS5 controller.")
            pygame.time.delay(1000)  # Wait for a second before retrying
        self.controller = pygame.joystick.Joystick(0)  # Assign the first joystick
        self.controller.init()
        print(f"Connected to controller: {self.controller.get_name()}")

    def init_serial(self):
        try:
            self.arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            print(f"Connected to Arduino on {SERIAL_PORT}")
        except serial.SerialException as e:
            print(f"Could not open serial port {SERIAL_PORT}: {e}")
            self.quit(1)

    def run(self):
        print("Running. Use Left Trigger to rotate claw, Right Trigger to open/close claw.")
        clock = pygame.time.Clock()
        while True:
            self.handle_triggers()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
            clock.tick(60)  # 60 FPS
    
    def handle_triggers(self):
        left_trigger = self.controller.get_axis(LEFT_TRIGGER)
        right_trigger = self.controller.get_axis(RIGHT_TRIGGER) 

        if abs(left_trigger) > TRIGGER_THRESHOLD and left_trigger>0 and left_trigger<180:
            self.rotate_claw(left_trigger)

        if abs(right_trigger) > TRIGGER_THRESHOLD and right_trigger>0 and right_trigger<180:
            self.adjust_claw(right_trigger)
        
    def rotate_claw(self, trigger_value):
        rotation_speed = trigger_value * 5  # Adjust multiplier based on desired speed
        self.roll_position += rotation_speed
        self.roll_position = max(ROLL_MIN, min(ROLL_MAX, self.roll_position))
        self.send_servo_command('roll', round(self.roll_position))
        print(f"Claw rotated to {round(self.roll_position)} degrees")
    
    def adjust_claw(self, trigger_value):
        target_position = CLAW_CLOSED + (trigger_value + 1) / 2 * (CLAW_OPEN - CLAW_CLOSED)
        self.claw_position = round(target_position)
        self.send_servo_command('claw', self.claw_position)
        print(f"Claw adjusted to {self.claw_position} degrees")

    def send_servo_command(self, servo, position):
        if not SEND_SERIAL:
            return

        command = f"{servo}:{position}\n"
        try:
            print(f"Sending serial: {command.strip()}")
            if self.arduino:  # Check if Arduino is connected
                self.arduino.write(command.encode('utf-8'))
            else:
                print("Arduino connection not established.")
        except Exception as e:
            print(f"Error sending data to Arduino: {e}")

    def quit(self, status=0):
        print("Exiting program...")
        if self.arduino is not None:  
            self.arduino.close()
        pygame.quit()
        sys.exit(status)

if __name__ == "__main__":
    program = MainProgram()
    program.run()
