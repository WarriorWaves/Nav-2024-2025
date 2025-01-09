import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QGroupBox, QProgressBar, QSizePolicy  
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from pygame_controller import ROVController 


class VideoFeedWidget(QLabel):
    def __init__(self, title="Video Feed", camera_index=0, parent=None):
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
        

        self.capture = cv2.VideoCapture(camera_index)
        
        if not self.capture.isOpened():
            print(f"Error: Could not open camera {camera_index}.")
        else:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_feed)
            self.timer.start(30)  

    def update_feed(self):
        """Update the video feed in the QLabel"""
        ret, frame = self.capture.read()
        if ret: 
            label_width = self.width()
            label_height = self.height()
            frame_height, frame_width = frame.shape[:2]
            aspect_ratio = frame_width / frame_height
            if label_width / label_height > aspect_ratio: 
                new_height = label_height
                new_width = int(new_height * aspect_ratio)
            else:
                new_width = label_width
                new_height = int(new_width / aspect_ratio)
            frame_resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            canvas = np.zeros((label_height, label_width, 3), dtype=np.uint8)
            x_offset = (label_width - new_width) // 2
            y_offset = (label_height - new_height) // 2
            canvas[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = frame_resized
            rgb_image = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
            h, w, c = rgb_image.shape
            bytes_per_line = c * w
            convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(convert_to_qt_format)
            self.setPixmap(pixmap)
        else:
            self.setText("No Signal")

    def closeEvent(self, event):
        """Ensure the camera is released when the widget is closed"""
        if self.capture.isOpened():
            self.capture.release()
        event.accept()

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

        self.indicator = QLabel("""CLOSED""")
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
        self.controller = ROVController()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.left_panel = QVBoxLayout()
        self.thruster_power_panel = ThrusterPowerPanel()
        self.left_panel.addWidget(self.thruster_power_panel)

        self.center_panel = QVBoxLayout()
        self.video_feed1 = VideoFeedWidget("Camera Feed 1", camera_index=0)  
        self.video_feed2 = VideoFeedWidget("Camera Feed 2", camera_index=1) 
        self.center_panel.addWidget(self.video_feed1)
        self.center_panel.addWidget(self.video_feed2)

        self.right_panel = QVBoxLayout()
        self.claw_status = ClawStatusWidget()
        self.right_panel.addWidget(self.claw_status)
        self.right_panel.addStretch() 
        self.main_layout.addLayout(self.left_panel)
        self.main_layout.addLayout(self.center_panel, stretch=2)  
        self.main_layout.addLayout(self.right_panel)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)  

        self.setWindowTitle("ROV Control Panel")
        self.setStyleSheet("background-color: #121212; color: white;")

    def update(self):
        """Update GUI elements based on joystick input"""
        self.controller.process_joystick()  

        thrust_values = self.controller.get_thrust_values()
        for i, thruster in enumerate(self.thruster_power_panel.thrusters):
            thruster.update_power(thrust_values[i] - 1500)  

    def closeEvent(self, event):
        """Override close event to clean up resources"""
        self.controller.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ROVControlPanel()
    window.show()
    sys.exit(app.exec_())