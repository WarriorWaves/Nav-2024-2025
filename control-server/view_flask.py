import os
import time
import serial
import sys
import cv2

SERIAL_PORT = '/dev/ttyUSB0'  
BAUD_RATE = 9600

try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    sys.exit(1)  

SEND_SERIAL = True

possible_cams = ["http://bob.local:5000/"]
caps = [cv2.VideoCapture(cam) for cam in possible_cams]

def capture_and_send_frames(cap):
    while True:
        try:
            success, frame = cap.read()  
            if not success:
                raise ValueError("Could not read frame from camera")
            
            ret, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()

            frame_size = len(frame_bytes)
            arduino.write(f"{frame_size}\n".encode())  
            arduino.write(frame_bytes) 
            
            time.sleep(0.1)  
        except ValueError as e:
            print("Error reading frame:", e)
            break

if __name__ == "__main__":
    try:
        print("Starting camera feed...")
        capture_and_send_frames(caps[0])
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        arduino.close()  
