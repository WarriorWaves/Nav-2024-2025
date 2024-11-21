import gi
import serial
import sys
from threading import Thread
from gi.repository import Gst, GLib

gi.require_version("Gst", "1.0")

Gst.init(None)

SERIAL_PORT = '/dev/ttyUSB0'  
BAUD_RATE = 9600

try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    sys.exit(1)  

SEND_SERIAL = True

pipeline = Gst.parse_launch(
    "appsrc name=source ! h264parse ! avdec_h264 ! videoconvert ! autovideosink"
)

pipeline.set_state(Gst.State.PLAYING)

appsrc = pipeline.get_by_name("source")

def read_serial_and_feed_pipeline():
    while SEND_SERIAL:
        try:
            frame_size = int(arduino.readline().decode().strip())
            
            frame_data = arduino.read(frame_size)
            
            buf = Gst.Buffer.new_wrapped(frame_data)
            appsrc.emit("push-buffer", buf)

        except Exception as e:
            print(f"Error reading frame from serial: {e}")
            break

    appsrc.emit("end-of-stream")

serial_thread = Thread(target=read_serial_and_feed_pipeline)
serial_thread.start()

loop = GLib.MainLoop()
try:
    loop.run()
except KeyboardInterrupt:
    pass

pipeline.set_state(Gst.State.NULL)
arduino.close()
