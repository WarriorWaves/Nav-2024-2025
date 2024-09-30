pip install pyserial
import serial
import time
import matplotlib.pyplot as plt

serial_port = "/dev/ttyUSB0"  
baud_rate = 9600 

ser = serial.Serial(serial_port, baud_rate, timeout=1)
lastmessage = ""

plt.ion()  
fig, ax = plt.subplots()

try:

    while True:
        newmessage = ""
        with open("./send.txt", "r") as f:
            newmessage = f.read().strip()

        print(f"last message: {lastmessage}")
        if newmessage != lastmessage:
            print(f"Sending new message: {newmessage}")
            ser.write(newmessage.encode())  # Send message to Arduino
            lastmessage = newmessage


        ser.write("xy".encode())

        if ser.in_waiting > 0:
            received_data = ser.readline().decode().strip()
            print(f"Received: {received_data}")

            try:
                depth = float(received_data.split("dd")[1].split("tt")[0])

                ax.plot(time.time(), depth, "ro")  # Plot a red dot for each depth value
                ax.set_xlim(time.time() - 10, time.time())  # Last 10 seconds on x-axis
                ax.set_ylim(-0.3, 2.5)  
                plt.draw()  
                plt.pause(0.01)  
            except (ValueError, IndexError):
                print("Error parsing received data")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Closing serial connection")
    ser.close()

finally:
    print("Closing serial connection")
    ser.close()
