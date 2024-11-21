import cv2
import serial
import time
import sys

SERIAL_PORT = '/dev/ttyUSB0'  
BAUD_RATE = 9600

try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    sys.exit(1)  

SEND_SERIAL = True

def capture_feed(camera_index):
    cap = cv2.VideoCapture(camera_index)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield cv2.imencode(".jpg", frame)[1].tobytes()

if __name__ == "__main__":
    cams = [0, 0]  
    camera_index = cams[0]  

    for frame in capture_feed(camera_index):
        arduino.write(frame)
        arduino.write(b'\n')  

        if arduino.in_waiting:
            response = arduino.readline()
            print("Received from serial:", response.decode().strip())
