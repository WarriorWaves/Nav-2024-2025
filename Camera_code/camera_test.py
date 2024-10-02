import serial
import time
import matplotlib.pyplot as plt

serial_port = "/dev/tty.usbmodem11101"  
baud_rate = 9600  

ser = serial.Serial(serial_port, baud_rate, timeout=1) 
lastmessage = ""  

# Prepare the plot
plt.ion()  
fig, ax = plt.subplots()

# Lists to store time and depth for plotting
times = []
depths = []

# Clear the send.txt file initially
with open("send.txt", "w") as file:
    file.write("") 

try:
    while True:
        newmessage = ""
        with open("./send.txt", "r") as f:
            newmessage = f.read().strip()  

        print(f"Last message: {lastmessage}")
        if newmessage != lastmessage:
            print(f"Sending new message: {newmessage}")
            ser.write(newmessage.encode()) 
            lastmessage = newmessage 

        ser.write("xy".encode())  

        if ser.in_waiting > 0:
            received_data = ser.readline().decode().strip()  
            print(f"Received: {received_data}")

            try:
                # Make sure your data is in the expected format
                depth = float(received_data.split("dd")[1].split("tt")[0])  
                
                # Append the current time and depth to the lists
                current_time = time.time()
                times.append(current_time)
                depths.append(depth)

                # Update the plot
                ax.clear()  # Clear previous points
                ax.plot(times[-10:], depths[-10:], "ro")  # Plot the last 10 points
                ax.set_xlim(current_time - 10, current_time)  
                ax.set_ylim(-0.3, 2.5)  
                ax.set_title("Depth Over Time")
                ax.set_xlabel("Time (s)")
                ax.set_ylabel("Depth (m)")
                plt.draw()  
                plt.pause(0.01)  
            except (ValueError, IndexError) as e:
                print("Error parsing received data:", e)  

        time.sleep(0.1)  
except KeyboardInterrupt:
    print("Closing serial connection")
    ser.close()  

finally:
    print("Closing serial connection")
    ser.close()  
