import os
import time
import serial
import sys
import cv2

# Initialize serial communication
SERIAL_PORT = '/dev/ttyUSB0'  # Update this with your Arduino's serial port
BAUD_RATE = 9600

# Exception handling for serial port opening
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    sys.exit(1)  # Exit the program if the serial port cannot be opened

SEND_SERIAL = True

# Possible camera URLs or indices
possible_cams = ["http://bob.local:5000/"]
caps = [cv2.VideoCapture(cam) for cam in possible_cams]

# Function to capture frames and send them over serial
def capture_and_send_frames(cap):
    while True:
        try:
            success, frame = cap.read()  # read the camera frame
            if not success:
                raise ValueError("Could not read frame from camera")
            
            # Encode the frame as JPEG
            ret, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()

            # Send frame size first, followed by the frame
            frame_size = len(frame_bytes)
            arduino.write(f"{frame_size}\n".encode())  # Send the size of the frame first
            arduino.write(frame_bytes)  # Send the actual frame data
            
            time.sleep(0.1)  # Optional: add delay for stability
        except ValueError as e:
            print("Error reading frame:", e)
            break

# Main function to run the camera streaming over serial
if __name__ == "__main__":
    try:
        print("Starting camera feed...")
        # Assuming the first camera for demonstration purposes
        capture_and_send_frames(caps[0])
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        arduino.close()  # Close the serial connection when done
