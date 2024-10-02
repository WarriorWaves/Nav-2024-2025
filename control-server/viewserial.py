import gi
import serial
import sys
from threading import Thread
from gi.repository import Gst, GLib

gi.require_version("Gst", "1.0")

# Initialize GStreamer
Gst.init(None)

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

# Define the GStreamer pipeline for serial input
pipeline = Gst.parse_launch(
    "appsrc name=source ! h264parse ! avdec_h264 ! videoconvert ! autovideosink"
)

# Start playing
pipeline.set_state(Gst.State.PLAYING)

# Get the appsrc element from the pipeline
appsrc = pipeline.get_by_name("source")

# Function to read video frames from the serial port and push them to GStreamer
def read_serial_and_feed_pipeline():
    while SEND_SERIAL:
        try:
            # Read frame size from serial (assuming size is sent as a string with newline)
            frame_size = int(arduino.readline().decode().strip())
            
            # Read the actual frame data
            frame_data = arduino.read(frame_size)
            
            # Create a GStreamer buffer and push the frame to the appsrc
            buf = Gst.Buffer.new_wrapped(frame_data)
            appsrc.emit("push-buffer", buf)

        except Exception as e:
            print(f"Error reading frame from serial: {e}")
            break

    # End the stream
    appsrc.emit("end-of-stream")

# Run the serial reading in a separate thread
serial_thread = Thread(target=read_serial_and_feed_pipeline)
serial_thread.start()

# GStreamer main loop to keep the pipeline running
loop = GLib.MainLoop()
try:
    loop.run()
except KeyboardInterrupt:
    pass

# Clean up
pipeline.set_state(Gst.State.NULL)
arduino.close()
