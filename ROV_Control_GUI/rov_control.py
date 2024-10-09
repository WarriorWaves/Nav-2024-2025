import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QProgressBar, QPushButton, QSlider, QGroupBox, QGridLayout, QComboBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont, QPainter, QColor, QPainterPath

class CustomProgressBar(QProgressBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setText_custom = ""

    def set_custom_text(self, text):
        self.setText_custom = text
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, self.setText_custom)

class HistoryWidget(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 100)  # Smaller size for compact window
        self.title = title
        self.data = []

    def add_data(self, value):
        self.data.append(value)
        if len(self.data) > 60:
            self.data.pop(0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        painter.fillRect(self.rect(), QColor(30, 30, 30))

        # Draw title
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(10, 20, self.title)

        # Draw graph
        if self.data:
            painter.setPen(QColor(61, 174, 233))
            path = QPainterPath()
            scale_x = self.width() / 60
            scale_y = (self.height() - 40) / 100

            path.moveTo(0, self.height() - 20 - self.data[0] * scale_y)
            for i, value in enumerate(self.data):
                x = i * scale_x
                y = self.height() - 20 - value * scale_y
                path.lineTo(x, y)

            painter.drawPath(path)

class ROVControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced ROV Control Panel")
        self.setGeometry(100, 100, 1200, 600)  # Adjusted window size
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QLabel { color: #ffffff; font-size: 14px; }
            QGroupBox { 
                color: #ffffff; 
                font-size: 16px; 
                font-weight: bold;
                border: 2px solid #3daee9;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QPushButton {
                background-color: #3daee9;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #43b0f1; }
            QComboBox {
                background-color: #2e2e2e;
                color: white;
                border: 1px solid #3daee9;
                padding: 5px;
                border-radius: 3px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #3daee9;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Left panel for video feeds and controls
        self.left_panel = QVBoxLayout()
        self.main_layout.addLayout(self.left_panel, 2)

        # Right panel for sensor data
        self.right_panel = QVBoxLayout()
        self.main_layout.addLayout(self.right_panel, 1)

        self.setup_video_feeds()
        self.setup_control_panel()
        self.setup_sensor_readouts()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all)
        self.timer.start(30)

    def setup_video_feeds(self):
        video_layout = QHBoxLayout()
        self.video_label1 = QLabel(self)
        self.video_label2 = QLabel(self)
        for label in [self.video_label1, self.video_label2]:
            label.setFixedSize(640, 480)  # Increased size for larger video feeds
            label.setStyleSheet("border: 2px solid #3daee9; border-radius: 5px;")
            video_layout.addWidget(label)
        self.left_panel.addLayout(video_layout)

        # Camera controls
        camera_control = QHBoxLayout()
        self.camera_selector = QComboBox()
        self.camera_selector.addItems(["Both Cameras", "Camera 1", "Camera 2"])
        camera_control.addWidget(QLabel("Camera View:"))
        camera_control.addWidget(self.camera_selector)
        self.left_panel.addLayout(camera_control)

    def setup_control_panel(self):
        control_group = QGroupBox("ROV Controls")
        control_layout = QGridLayout()
        control_group.setLayout(control_layout)

        # Thruster controls
        self.thruster_sliders = {}
        for i, direction in enumerate(["Forward", "Backward", "Left", "Right", "Up", "Down"]):
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(0)
            label = QLabel(f"{direction}: 0%")
            slider.valueChanged.connect(lambda value, l=label, d=direction: l.setText(f"{d}: {value}%"))
            control_layout.addWidget(QLabel(direction), i, 0)
            control_layout.addWidget(slider, i, 1)
            control_layout.addWidget(label, i, 2)
            self.thruster_sliders[direction] = slider

        # Additional controls
        self.light_slider = QSlider(Qt.Horizontal)
        self.light_slider.setRange(0, 100)
        control_layout.addWidget(QLabel("Lights"), 6, 0)
        control_layout.addWidget(self.light_slider, 6, 1)
        control_layout.addWidget(QLabel("0%"), 6, 2)
        self.light_slider.valueChanged.connect(lambda value: control_layout.itemAtPosition(6, 2).widget().setText(f"{value}%"))

        self.arm_button = QPushButton("Deploy Arm")
        self.arm_button.clicked.connect(self.toggle_arm)
        control_layout.addWidget(self.arm_button, 7, 0, 1, 3)

        self.left_panel.addWidget(control_group)

    def setup_sensor_readouts(self):
        sensor_group = QGroupBox("Sensor Readouts")
        sensor_layout = QVBoxLayout()
        sensor_group.setLayout(sensor_layout)

        self.temp_bar = CustomProgressBar()
        self.depth_bar = CustomProgressBar()
        self.pressure_bar = CustomProgressBar()

        for bar in [self.temp_bar, self.depth_bar, self.pressure_bar]:
            bar.setRange(0, 100)
            bar.setTextVisible(False)
            bar.setFixedHeight(30)
            sensor_layout.addWidget(bar)

        self.right_panel.addWidget(sensor_group)

    def update_all(self):
        self.update_video_feed()
        self.update_sensor_readings()

    def update_video_feed(self):
        for label in [self.video_label1, self.video_label2]:
            image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            h, w, ch = image.shape
            bytes_per_line = ch * w
            qt_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            label.setPixmap(QPixmap.fromImage(qt_image))

    def update_sensor_readings(self):
        temp = np.random.randint(0, 100)
        depth = np.random.randint(0, 100)
        pressure = np.random.randint(0, 100)

        self.temp_bar.setValue(temp)
        self.temp_bar.set_custom_text(f"Temperature: {temp}°C")
        self.depth_bar.setValue(depth)
        self.depth_bar.set_custom_text(f"Depth: {depth}m")
        self.pressure_bar.setValue(pressure)
        self.pressure_bar.set_custom_text(f"Pressure: {pressure}kPa")

    def toggle_arm(self):
        if self.arm_button.text() == "Deploy Arm":
            self.arm_button.setText("Retract Arm")
        else:
            self.arm_button.setText("Deploy Arm")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ROVControlPanel()
    window.show()
    sys.exit(app.exec_())
