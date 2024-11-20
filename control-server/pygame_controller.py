import serial
import pygame
import time

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


class IMU:
    def __init__(self, port='/dev/ttyUSB0', baud_rate=9600):
        """Initialize the IMU class using serial communication."""
        self.serial_connection = serial.Serial(port, baud_rate)
        time.sleep(2)  # Wait for Arduino to initialize

    def read_imu(self):
        """Read accelerometer and gyroscope data from the IMU."""
        try:
            data = self.serial_connection.readline().decode('utf-8').strip()
            parts = data.split()
            accel_x = int(parts[2])
            accel_y = int(parts[4])
            accel_z = int(parts[6])
            gyro_x = int(parts[8])
            gyro_y = int(parts[10])
            gyro_z = int(parts[12])
            return {
                "accel": (accel_x, accel_y, accel_z),
                "gyro": (gyro_x, gyro_y, gyro_z),
            }
        except Exception as e:
            print(f"Error reading IMU: {e}")
            return None


class ROVController:
    def __init__(self, pid):
        pygame.init()
        pygame.joystick.init()

        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            print("No joystick detected!")

        try:
            self.arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        except serial.SerialException as e:
            print(f"Could not open serial port {SERIAL_PORT}: {e}")
            self.arduino = None

        self.current_thrust_values = [1500] * 6
        self.pid = pid
        self.imu = IMU(port=SERIAL_PORT, baud_rate=BAUD_RATE)  # IMU instance

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
        pygame.event.pump()  

        if self.joystick:
            surge = self.joystick.get_axis(1)  # Forward/Backward
            sway = self.joystick.get_axis(0)   # Left/Right
            heave = self.joystick.get_axis(2)  # Up/Down
            yaw = self.joystick.get_axis(3)    # Rotation

            imu_data = self.imu.read_imu()
            if imu_data:
                gyro_x, gyro_y, gyro_z = imu_data["gyro"]
                print(f"IMU Gyro Data: X={gyro_x}, Y={gyro_y}, Z={gyro_z}")

                # Example stabilization adjustment based on IMU gyro data
                yaw_correction = gyro_z / 100.0  
                yaw -= yaw_correction  # Adjust joystick yaw by IMU gyro

            # Calculate combined thrust for each motor
            combined_thrust = {
                "FR": surge - yaw - sway,  # Front Right
                "FL": surge + yaw + sway,  # Front Left
                "BR": surge - yaw + sway,  # Back Right
                "BL": surge + yaw - sway,  # Back Left
                "F": heave,  # Front (y-axis)
                "B": heave,  # Back (y-axis)
            }

            depth_correction = self.pid.compute_depth_correction()

            combined_thrust["F"] += depth_correction
            combined_thrust["B"] += depth_correction

            combined = [0] * 6
            for key, value in combined_thrust.items():
                idx = MAPPING_DICT[key]
                combined[idx] = int(1500 + (value * 75))  
                combined[idx] = min(max(combined[idx], 1500), 1650)  

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


# Replace with your PID implementation
class PIDController:
    def compute_depth_correction(self):
        return 0  


# Main
if __name__ == "__main__":
    pid = PIDController()
    rov = ROVController(pid)

    try:
        while True:
            rov.process_joystick()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        rov.close()
