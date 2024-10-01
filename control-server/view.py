import cv2
import serial
import time

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

# Capture the camera feed
def capture_feed(camera_index):
    cap = cv2.VideoCapture(camera_index)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield cv2.imencode(".jpg", frame)[1].tobytes()

if __name__ == "__main__":
    cams = [0, 0]  # List of camera indices
    camera_index = cams[0]  # Choose the camera index to use

    # Start capturing frames
    for frame in capture_feed(camera_index):
        # Send frame data over serial
        aruindo.write(frame)
        aruindo.write(b'\n')  # Optional: add a delimiter for frame separation

        # Optional: read responses from serial if needed
        if aruindo.in_waiting:
            response = aruindo.readline()
            print("Received from serial:", response.decode().strip())
