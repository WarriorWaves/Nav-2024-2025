import serial
import time

class IMU:
    def __init__(self, port='/dev/ttyUSB0', baud_rate=9600):
        """
        Initialize the IMU class using serial communication.
        :param port: The serial port the Arduino is connected to (default: '/dev/ttyUSB0').
        :param baud_rate: The baud rate for serial communication (default: 9600).
        """
        self.serial_connection = serial.Serial(port, baud_rate)
        time.sleep(2)  

    def read_imu(self):
        """
        Read accelerometer and gyroscope data from the serial data sent by the Arduino.
        :return: A dictionary with accelerometer and gyroscope data.
        """
        data = self.serial_connection.readline().decode('utf-8').strip()  # Read the data from Arduino
        # Example data: "Accel X: 12345 Y: -12345 Z: 12345 | Gyro X: 54321 Y: -54321 Z: 54321"
        # Split the string to get the values
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

# Example usage
imu = IMU(port='/dev/ttyUSB0', baud_rate=9600)  # Update port based on your system
while True:
    imu_data = imu.read_imu()
    print(imu_data)
    time.sleep(1)
