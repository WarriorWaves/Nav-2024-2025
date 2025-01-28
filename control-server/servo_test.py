import pygame
import serial
import time

class ClawServoController:
    def __init__(self, serial_port='/dev/ttyUSB0', baud_rate=9600):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Connected to controller: {self.joystick.get_name()}")
        else:
            raise Exception("No controller found!")

        try:
            self.serial = serial.Serial(serial_port, baud_rate, timeout=1)
            print(f"Connected to PCB on {serial_port}")
            time.sleep(2)
        except serial.SerialException as e:
            raise Exception(f"Failed to connect to PCB: {e}")

    def claw_test(self):
        print("\nClaw Servo Test Mode")
        print("Use R2/L2 triggers for open/close and right stick left/right for rotation")
        print("Press Ctrl+C to exit")

        try:
            while True:
                pygame.event.pump()

                # Get trigger values (R2/L2)
                open_value = (self.joystick.get_axis(5) + 1) / 2  # Normalize R2 (0 to 1)
                close_value = (self.joystick.get_axis(2) + 1) / 2  # Normalize L2 (0 to 1)

                # Get right stick horizontal axis for rotation
                rotation_value = self.joystick.get_axis(3)  # Right stick left/right

                # Calculate PWM values
                open_pwm = int(1500 + (open_value * 500))  # Open servo: 1500-2000
                close_pwm = int(1500 - (close_value * 500))  # Close servo: 1500-1000
                rotation_pwm = int(1500 + (rotation_value * 500))  # Rotation servo: 1000-2000

                # Send commands
                self.send_command('open', open_pwm)
                self.send_command('close', close_pwm)
                self.send_command('rotate', rotation_pwm)

                print(f"Open PWM: {open_pwm}, Close PWM: {close_pwm}, Rotate PWM: {rotation_pwm}")

                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nTest ended by user")
            self.send_command('neutral', 1500)  # Neutral position for all servos
        finally:
            self.close()

    def send_command(self, servo, value):
        """Send PWM command to PCB (Arduino)"""
        try:
            command = f"{servo}:{value}\n"
            self.serial.write(command.encode('utf-8'))
        except Exception as e:
            print(f"\nError sending command: {e}")

    def close(self):
        """Clean up resources"""
        self.send_command('neutral', 1500)  # Neutral position
        self.serial.close()
        pygame.quit()

if __name__ == "__main__":
    try:
        controller = ClawServoController(serial_port='/dev/ttyUSB0')  # Adjust serial port as needed
        controller.claw_test()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'controller' in locals():
            controller.close()
