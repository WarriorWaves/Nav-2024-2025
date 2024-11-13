import time
import subprocess
import serial
import sys

# Initialize serial communication
SERIAL_PORT = '/dev/ttyUSB0'  # Update this with your Arduino's serial port
BAUD_RATE = 9600
arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

try:
  arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
  print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    sys.exit(1)

def runStuff():
  try:
    while True:
      if arduino.in_waiting > 0:
        serial_data = arduino.readline().decode('utf-8')  # Read and decode the serial data
        print(f"Received: {serial_data}")
      time.sleep(0.1);
  except KeyboardInterrupt:
    print("Keyboard hit")
    arduino.close()


runStuff()
    
