import sys
import time
import subprocess
import os
import power_comp
import serial

# Initialize serial communication
SERIAL_PORT = '/dev/ttyUSB0'  # Update this with your Arduino's serial port
BAUD_RATE = 9600
arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

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
        serial_data = arduino.readLine().decode('utf-8')
        process_serial_input(serial_data)
      time.sleep(0.1)
  except KeyboardInterrupt:
    print("Keyboard hit")
  finally:
    arduino.close()

run_stuff()
    
      
