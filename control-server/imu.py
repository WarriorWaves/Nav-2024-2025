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
        data = self.serial_connection.readline().decode('utf-8').strip()  
        print(f"Received data: {data}") 
        
        parts = data.split('|')  
        
        if len(parts) != 2:
            print("Error: Data format is incorrect.")
            return None
        
        accel_data = parts[0].split()  
        gyro_data = parts[1].split()   
        
        # Extract accelerometer and gyroscope values
        accel_x = int(accel_data[2].split(":")[1])  # Accel X value
        accel_y = int(accel_data[4].split(":")[1])  # Accel Y value
        accel_z = int(accel_data[6].split(":")[1])  # Accel Z value
        
        gyro_x = int(gyro_data[2].split(":")[1])   # Gyro X value
        gyro_y = int(gyro_data[4].split(":")[1])   # Gyro Y value
        gyro_z = int(gyro_data[6].split(":")[1])   # Gyro Z value
        
        return {
            "accel": (accel_x, accel_y, accel_z),
            "gyro": (gyro_x, gyro_y, gyro_z),
        }

imu = IMU(port='/dev/ttyUSB0', baud_rate=9600)  
