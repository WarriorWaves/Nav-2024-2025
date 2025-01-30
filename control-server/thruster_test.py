import pygame
import serial
import time

class ThrusterController:
    def __init__(self, serial_port='/dev/tty.usbserial-120', baud_rate=9600):
        pygame.init()
        pygame.joystick.init()
        
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Connected to controller: {self.joystick.get_name()}")
        else:
            raise Exception("No controller found!!!!!!!!!")

        try:
            self.serial = serial.Serial(serial_port, baud_rate, timeout=1)
            print(f"Connected to PCB on {serial_port}")
            time.sleep(2)
        except serial.SerialException as e:
            raise Exception(f"Failed to connect to PCB: {e}")

    def controller_test(self):
        print("\nController Test Mode")
        print("Use the left stick up/down to control the thruster")
        print("Press Ctrl+C to exit")

        dead_zone = 0.05  # Adjust dead zone threshold
        try:
            while True:
                pygame.event.pump()
                
                # Get the joystick stick value (left axis vertical is axis 1)
                stick_value = self.joystick.get_axis(1)
                print(f"Stick Value: {stick_value}")  # Debugging joystick value
                
                # Apply dead zone
                if abs(stick_value) < dead_zone:
                    stick_value = 0

                # Calculate thrust value based on joystick input, adjusted for better scaling
                thrust_value = int(1500 + (stick_value * 200))  # Increased scaling range for better control
                thrust_value = min(max(thrust_value, 1100), 1900)  # Ensuring it stays within valid range

                print(f"Sending PWM value: {thrust_value}")
                
                # Send the PWM value to Arduino
                self.send_command(thrust_value)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nTest ended by user")
            self.send_command(1500)  # Send neutral value when exiting
        finally:
            self.close()

    def send_command(self, value):
        """Send PWM command to PCB (Arduino)"""
        try:
            self.serial.write(f"{value}\n".encode('utf-8'))
            self.serial.flush()  # Ensure the data is sent immediately
            print(f"Sent PWM value: {value}")  # Debugging serial send
        except Exception as e:
            print(f"\nError sending command: {e}")

    def close(self):
        """Clean up resources"""
        self.send_command(1500)  # Send neutral value on exit
        self.serial.close()
        pygame.quit()

if __name__ == "__main__":
    try:
        controller = ThrusterController(serial_port='/dev/tty.usbserial-120') 
        controller.controller_test()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'controller' in locals():
            controller.close()
