import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QGroupBox, QGridLayout, QSizePolicy, QProgressBar
)
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont
import pygame


class JoystickController:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        # Initialize the first joystick
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            self.joystick = None
            print("No joystick detected")

        self.thruster_powers = [0] * 6
        self.claw_is_open = False

    def process_joystick(self):
        if not self.joystick:
            return

        pygame.event.pump()

        # Get joystick values
        x = self.joystick.get_axis(0)  # Left/Right
        y = self.joystick.get_axis(1)  # Forward/Backward
        z = self.joystick.get_axis(2)  # Up/Down
        rotate = self.joystick.get_axis(3)  # Rotation

        # Process button for claw
        if self.joystick.get_button(0):  # Assuming button 0 controls the claw
            self.claw_is_open = not self.claw_is_open

        # Calculate thruster powers based on joystick input
        self.thruster_powers[0] = int((y + rotate) * 100)  # Front Left
        self.thruster_powers[1] = int((y - rotate) * 100)  # Front Right
        self.thruster_powers[2] = int((y + rotate) * 100)  # Back Left
        self.thruster_powers[3] = int((y - rotate) * 100)  # Back Right
        self.thruster_powers[4] = int(z * 100)  # Vertical Left
        self.thruster_powers[5] = int(z * 100)  # Vertical Right

        # Clamp values between -100 and 100
        self.thruster_powers = [max(-100, min(100, p)) for p in self.thruster_powers]

    def get_thruster_powers(self):
        return self.thruster_powers

    def get_claw_status(self):
        return self.claw_is_open

    def close(self):
        pygame.quit()


class VideoFeedWidget(QLabel):
    def __init__(self, title="Video Feed", parent=None):
        super().__init__(parent)
        self.setMinimumSize(480, 360)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            border: 2px solid #3d3d3d;
            border-radius: 8px;
            padding: 5px;
            background-color: #2d2d2d;
        """)
        self.setText(f"{title}\nNo Signal")


class ThrusterPowerWidget(QWidget):
    def __init__(self, thruster_num, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)

        self.title = QLabel(f"T{thruster_num}")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Arial", 10, QFont.Bold))

        self.power_bar = QProgressBar()
        self.power_bar.setOrientation(Qt.Vertical)
        self.power_bar.setRange(-100, 100)
        self.power_bar.setValue(0)
        self.power_bar.setTextVisible(False)
        self.power_bar.setMinimumHeight(100)

        self.power_label = QLabel("0%")
        self.power_label.setAlignment(Qt.AlignCenter)
        self.power_label.setFont(QFont("Arial", 9))

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.power_bar)
        self.layout.addWidget(self.power_label)

    def update_power(self, power):
        self.power_bar.setValue(int(power))
        self.power_label.setText(f"{int(power)}%")

        if power > 0:
            chunk_style = """
                QProgressBar::chunk {
                    background-color: qlineargradient(
                        x1: 0, y1: 0,
                        x2: 0, y2: 1,
                        stop: 0 #4CAF50,
                        stop: 0.5 #81C784,
                        stop: 1 #4CAF50
                    );
                }
            """
        elif power < 0:
            chunk_style = """
                QProgressBar::chunk {
                    background-color: qlineargradient(
                        x1: 0, y1: 0,
                        x2: 0, y2: 1,
                        stop: 0 #f44336,
                        stop: 0.5 #e57373,
                        stop: 1 #f44336
                    );
                }
            """
        else:
            chunk_style = """
                QProgressBar::chunk {
                    background-color: #424242;
                }
            """

        self.power_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                background-color: #2d2d2d;
            }
        """ + chunk_style)


class ThrusterPowerPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Thruster Power", parent)
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(15)

        self.thrusters = []
        for i in range(6):
            thruster = ThrusterPowerWidget(i + 1)
            self.thrusters.append(thruster)
            self.layout.addWidget(thruster)

        self.setStyleSheet("""
            QGroupBox {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 8px;
                margin-top: 1em;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: white;
            }
        """)


class ClawStatusWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)

        self.status_label = QLabel("CLAW STATUS:")
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))

        self.indicator = QLabel("CLOSED")
        self.indicator.setFont(QFont("Arial", 12, QFont.Bold))
        self.indicator.setStyleSheet("color: #ff4444;")

        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.indicator)
        self.layout.setContentsMargins(20, 10, 20, 10)

    def update_status(self, is_open):
        self.indicator.setText("OPEN" if is_open else "CLOSED")
        self.indicator.setStyleSheet(
            "color: #4CAF50;" if is_open else "color: #ff4444;"
        )


class ROVControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROV Control Panel")
        self.setGeometry(100, 100, 1600, 900)

        # Initialize controller
        self.controller = JoystickController()

        # Setup UI
        self.setup_ui()

        # Start update timer (30 fps)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all)
        self.timer.start(33)

        # Initialize video captures
        self.stream1 = cv2.VideoCapture(0)
        self.stream2 = cv2.VideoCapture(1)

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)

        video_container = QWidget()
        video_layout = QHBoxLayout(video_container)
        video_layout.setSpacing(10)

        self.video_feed1 = VideoFeedWidget("Main Camera")
        self.video_feed2 = VideoFeedWidget("Secondary Camera")
        video_layout.addWidget(self.video_feed1)
        video_layout.addWidget(self.video_feed2)

        self.thruster_power_panel = ThrusterPowerPanel()

        control_container = QWidget()
        control_layout = QHBoxLayout(control_container)

        left_controls = QVBoxLayout()

        emergency_group = QGroupBox("Emergency Controls")
        emergency_layout = QHBoxLayout()
        emergency_button = QPushButton("EMERGENCY SURFACE")
        emergency_button.setStyleSheet("""
            QPushButton {
                background-color: #c62828;
                font-weight: bold;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        emergency_layout.addWidget(emergency_button)
        emergency_group.setLayout(emergency_layout)

        left_controls.addWidget(emergency_group)
        left_controls.addStretch()

        control_layout.addLayout(left_controls)
        control_layout.addWidget(self.thruster_power_panel)

        main_layout.addWidget(video_container)
        main_layout.addLayout(control_layout)

        self.claw_status_widget = ClawStatusWidget()
        main_layout.addWidget(self.claw_status_widget)

    def update_all(self):
        self.controller.process_joystick()
        thruster_powers = self.controller.get_thruster_powers()
        claw_status = self.controller.get_claw_status()

        # Update thruster powers
        for i, power in enumerate(thruster_powers):
            self.thruster_power_panel.thrusters[i].update_power(power)

        # Update claw status
        self.claw_status_widget.update_status(claw_status)

        # Update video feeds
        self.update_video_feed(self.video_feed1, self.stream1)
        self.update_video_feed(self.video_feed2, self.stream2)

    def update_video_feed(self, video_widget, stream):
        ret, frame = stream.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            video_widget.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        self.controller.close()
        self.stream1.release()
        self.stream2.release()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ROVControlPanel()
    window.show()
    sys.exit(app.exec_())
