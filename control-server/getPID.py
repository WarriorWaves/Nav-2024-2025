import time
import subprocess
import serial

# Initialize serial communication
SERIAL_PORT = '/dev/ttyUSB0'  # Update this with your Arduino's serial port
BAUD_RATE = 9600
arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

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
    
