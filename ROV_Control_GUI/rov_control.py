import sys
import time
import serial
import pygame
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QGroupBox, QPushButton
)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal

# Constants for serial communication
SERIAL_PORT = '/dev/ttyUSB0'  # update with the correct port 
BAUD_RATE = 9600
SEND_SERIAL = True
RUN_THRUSTER = True

# Thruster mapping
MAPPING = [
    {"name": "OFR", "index": 0},
    {"name": "IFR", "index": 1},
    {"name": "IBR", "index": 2},
    {"name": "IBL", "index": 3},
    {"name": "OFL", "index": 4},
    {"name": "OBR", "index": 5},
]

MAPPING_DICT = {item["name"]: item["index"] for item in MAPPING}

class JoystickThread(QThread):
    # Signal to send the message to the GUI
    update_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.maxThrottle = 0.5
        self.curMessage = ""
        self.arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

    def run(self):
        pygame.init()
        pygame.joystick.init()
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

        while self.running:
            self.control(joystick)
            time.sleep(0.1)  # Prevent excessive CPU usage

    def control(self, joystick):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
                return
            elif event.type == pygame.JOYAXISMOTION:
                # Get joystick input
                surge = joystick.get_axis(1)
                sway = joystick.get_axis(0)
                heave = joystick.get_axis(2)
                yaw = joystick.get_axis(3)

                # Normalize thrust values
                combined_thrust = {
                    "OFR": surge - yaw - sway,
                    "IFR": heave,
                    "IBR": heave,
                    "IBL": heave,
                    "OFL": surge + yaw + sway,
                    "OBR": surge + yaw - sway,
                }

                combined = [0] * 6
                for key, value in combined_thrust.items():
                    combined[MAPPING_DICT[key]] = value

                # Format and send message
                self.curMessage = self.format_message(combined)
                self.send_serial()
                self.update_message.emit(self.curMessage)  # Emit the message

    def format_message(self, message):
        if RUN_THRUSTER:
            output = "c"
        else:
            output = "c," + ",".join("1500" for _ in message)
        return output + "," + ",".join(map(str, message))

    def send_serial(self):
        if SEND_SERIAL:
            try:
                self.arduino.write((self.curMessage + '\n').encode('utf-8'))
            except Exception as e:
                print(f"Error sending data to Arduino: {e}")

    def stop(self):
        self.running = False
        self.arduino.close()
        pygame.quit()


class ROVControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROV Control Panel")
        self.setGeometry(100, 100, 1200, 600)
        
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.setup_control_panel()

        # Initialize the joystick thread
        self.joystick_thread = JoystickThread()
        self.joystick_thread.update_message.connect(self.display_message)  # Connect the signal
        self.joystick_thread.start()  # Start the joystick thread

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)  # Adjust based on how frequently you want to update

    def setup_control_panel(self):
        control_group = QGroupBox("ROV Controls")
        control_layout = QVBoxLayout(control_group)

        self.thruster_sliders = {}
        for direction in ["Forward", "Backward", "Left", "Right", "Up", "Down"]:
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(0)
            control_layout.addWidget(QLabel(direction))
            control_layout.addWidget(slider)
            self.thruster_sliders[direction] = slider

        self.main_layout.addWidget(control_group)

        # Display message area
        self.message_label = QLabel("Current Message:")
        self.main_layout.addWidget(self.message_label)

    def display_message(self, message):
        self.message_label.setText(f"Current Message: {message}")

    def update(self):
        # Here you can update your GUI based on ROV status or joystick values
        pass

    def closeEvent(self, event):
        self.joystick_thread.stop()  # Stop the thread on close
        event.accept()  # Accept the close event


def main():
    app = QApplication(sys.argv)

    # Create and show the GUI
    gui = ROVControlPanel()
    gui.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
