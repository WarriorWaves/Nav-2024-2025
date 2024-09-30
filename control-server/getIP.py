import sys
import time
import subprocess
import os
import power_comp
import serial

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

ipsfound = []

def process_serial_input(data):
    curip = data.strip()  # Clean up the incoming data (removes newline, spaces, etc.)
    if curip not in ipsfound:
        ipsfound.append(curip)
        print(f"New IP found: {curip}")

def run_stuff():
    try:
        while True:
            if arduino.in_waiting > 0:
                serial_data = arduino.readline().decode('utf-8')  # Corrected to readline()
                process_serial_input(serial_data)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Keyboard hit")
    finally:
        arduino.close()  # Ensure the serial port is closed on exit
        print("Serial port closed.")

run_stuff()
