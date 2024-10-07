import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

class ROVControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROV Control Panel")
        self.setGeometry(100, 100, 1200, 480)  # Set initial size of the window
        self.setStyleSheet("background-color: #003366;")  # Dark blue background color

        # Central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Horizontal layout for video feeds
        self.video_layout = QHBoxLayout()
        self.main_layout.addLayout(self.video_layout)

        # Video Feed Display for Camera 1
        self.video_label1 = QLabel(self)
        self.video_label1.setFixedSize(640, 480)  # Set the size for Camera 1
        self.video_label1.setStyleSheet("border: 4px solid #008CBA; border-radius: 10px;")  # Blue border with rounded edges
        self.video_layout.addWidget(self.video_label1)

        # Video Feed Display for Camera 2
        self.video_label2 = QLabel(self)
        self.video_label2.setFixedSize(640, 480)  # Set the size for Camera 2
        self.video_label2.setStyleSheet("border: 4px solid #FF5733; border-radius: 10px;")  # Orange border with rounded edges
        self.video_layout.addWidget(self.video_label2)

        # Sensor Readouts (Temperature and Depth)
        self.temp_label = QLabel("Temperature: N/A", self)
        self.depth_label = QLabel("Depth: N/A", self)
        self.temp_label.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold; background-color: #00509E; padding: 10px; border-radius: 5px;")
        self.depth_label.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold; background-color: #00509E; padding: 10px; border-radius: 5px;")
        self.main_layout.addWidget(self.temp_label)
        self.main_layout.addWidget(self.depth_label)

        # Thruster Readings and Mapping
        self.thruster_label = QLabel("Thruster Power: N/A", self)
        self.thruster_mapping = QProgressBar(self)
        self.thruster_mapping.setOrientation(Qt.Horizontal)
        self.thruster_mapping.setRange(0, 100)
        self.thruster_mapping.setStyleSheet(
            "QProgressBar { background-color: #D9D9D9; border-radius: 5px; } "
            "QProgressBar::chunk { background-color: #76C7C0; border-radius: 5px; }"
        )
        self.thruster_label.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold; background-color: #00509E; padding: 10px; border-radius: 5px;")
        self.main_layout.addWidget(self.thruster_label)
        self.main_layout.addWidget(self.thruster_mapping)

        # Initialize camera captures (commented out for testing without actual camera)
        # self.capture1 = cv2.VideoCapture(0)  # Camera 1
        # self.capture2 = cv2.VideoCapture(1)  # Camera 2

        # Set initial values to "N/A"
        self.temp_label.setText("Temperature: N/A")
        self.depth_label.setText("Depth: N/A")
        self.thruster_label.setText("Thruster Power: N/A")
        self.thruster_mapping.setValue(0)

        # Timer for updating video feed and sensor data
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all)
        self.timer.start(30)  # Update every 30 ms for low latency

    def update_all(self):
        self.update_video_feed()
        self.update_sensor_readings()
        self.update_thruster_readings()

    def update_video_feed(self):
        # Update Camera 1 Feed
        # self.update_camera_feed(self.capture1, self.video_label1)
        # Update Camera 2 Feed
        # self.update_camera_feed(self.capture2, self.video_label2)
        pass  # Pass for testing without actual camera

    def update_camera_feed(self, capture, label):
        ret, frame = capture.read()
        if ret:
            # Convert frame to RGB for PyQt
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        # self.capture1.release()  # Release camera 1
        # self.capture2.release()  # Release camera 2
        event.accept()

    def update_sensor_readings(self):
        # Replace with actual sensor communication code
        pass  # Pass for testing without actual sensor data

    def update_thruster_readings(self):
        # Replace with actual thruster reading code
        pass  # Pass for testing without actual thruster data

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create a QApplication instance
    window = ROVControlPanel()  # Create an instance of the ROVControlPanel
    window.show()  # Show the window
    sys.exit(app.exec_())  # Execute the application
