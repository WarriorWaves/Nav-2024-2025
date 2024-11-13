import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QGroupBox, QProgressBar, QSizePolicy  # Add QSizePolicy here
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from pygame_controller import ROVController  # Import the ROVController class


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

        # Initialize ROV Controller
        self.controller = ROVController()

        # Set up the main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create and add widgets
        self.video_feed1 = VideoFeedWidget("Camera Feed 1")
        self.video_feed2 = VideoFeedWidget("Camera Feed 2")
        self.thruster_power_panel = ThrusterPowerPanel()
        self.claw_status = ClawStatusWidget()

        self.layout.addWidget(self.video_feed1)
        self.layout.addWidget(self.video_feed2)
        self.layout.addWidget(self.thruster_power_panel)
        self.layout.addWidget(self.claw_status)

        # Set up the timer to update joystick input and GUI
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)  # Update every 100ms

        self.setWindowTitle("ROV Control Panel")
        self.setStyleSheet("background-color: #121212; color: white;")

    def update(self):
        """Update GUI elements based on joystick input"""
        self.controller.process_joystick()  # Update thrust values

        # Update thruster power displays
        thrust_values = self.controller.get_thrust_values()
        for i, thruster in enumerate(self.thruster_power_panel.thrusters):
            thruster.update_power(thrust_values[i] - 1500)  # Adjust for 0% = 1500

    def closeEvent(self, event):
        """Override close event to clean up resources"""
        self.controller.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ROVControlPanel()
    window.show()
    sys.exit(app.exec_())
