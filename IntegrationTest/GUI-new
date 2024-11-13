
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QComboBox, QPushButton, QLineEdit, QMessageBox, QRadioButton, QHBoxLayout, QButtonGroup, QTextEdit
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QImage
from PyQt5.QtCore import QThread, pyqtSignal, QProcess, QTimer, QRect, Qt
import numpy as np
import sys
import math
import subprocess
import os
import time
import re

scx = 1
scy = 1
font_title = QFont('Arial', 20)
font_title.setBold(True)
#scale_x = 1
#scale_y = 1

font_button = QFont('Arial', 14)
font_dashboard = QFont('Arial', 14)

class RedirectedOutput: 
    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, message):
        # Append text to QTextEdit
        self.text_edit.append(message)

    def flush(self):
        pass  # Flush method can be empty for this purpose

class BackendWorker(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, abs_x, abs_y):
        super().__init__()
        self.abs_x = abs_x
        self.abs_y = abs_y

    def run(self):
        try:
            # Run the backend algorithm as a subprocess
            result = subprocess.run(
                ['python', 'dwa_astar_v5_user_input_obs.py', str(self.abs_x), str(self.abs_y)],
                capture_output=True, text=True
            )

            # Emit the result once the process completes
            if result.returncode == 0:
                self.result_ready.emit(result.stdout)
            else:
                self.result_ready.emit(f"Error: {result.stderr}")

        except Exception as e:
            self.result_ready.emit(f"Exception: {str(e)}")

class Map(QWidget):
    start_click_enabled = pyqtSignal()  # Signal to enable startpoint click
    end_click_enabled = pyqtSignal()  # Signal to enable endpoint click
    local_obstacle_click_enabled = pyqtSignal()  # Signal to enable local obstacle click
    startpoint_click_enabled = False # Flag to check if map click is enabled
    endpoint_click_enabled = False
    local_obstacle_point_click_enabled = False


    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("color: lightblue; border: 2px solid black; padding: 1px;")
        self.setGeometry(50, 80, 600, 600)
        self.dots = []  # List to store dots as relative positions (percentage of the width and height)
        self.startpoint = []
        self.endpoint = []
        self.background_image = None

        self.start_click_enabled.connect(self.enable_startpoint_click)
        self.end_click_enabled.connect(self.enable_endpoint_click)
        self.local_obstacle_click_enabled.connect(self.enable_local_obstacle_click)

    def load_background_image(self, image_path):
        self.background_image = QPixmap(image_path)
        self.update()

    def enable_startpoint_click(self):
        self.startpoint_click_enabled = True

    def enable_endpoint_click(self):
        self.endpoint_click_enabled = True

    def enable_local_obstacle_click(self):
        self.local_obstacle_point_click_enabled = True

    def mousePressEvent(self, event):    
        # Get the current size of the map
        map_width = self.width()
        map_height = self.height()

        # Calculate the relative position as a percentage of the map size
        dot_relative_x = (event.x() / map_width)/scx
        dot_relative_y = (event.y() / map_height)/scy

        relative_x = (event.x()/10)/scx
        relative_y = ((map_height - event.y())/10)/scy
        
        print("x-coord", relative_x)
        print("y-coord", relative_y)
        print("scale_x", scx)
        print("scale_y", scy)

        if self.startpoint_click_enabled:
            # Save the coordinates to a file
            self.save_start_point_to_file(relative_x, relative_y)
            self.startpoint.append((dot_relative_x, dot_relative_y))
            self.update()

            # Disable further clicks on the map
            self.startpoint_click_enabled = False

        elif self.endpoint_click_enabled:
            # Save the coordinates to a file
            self.save_end_point_to_file(relative_x, relative_y)
            self.endpoint.append((dot_relative_x, dot_relative_y))
            self.update()

            # Disable further clicks on the map
            self.endpoint_click_enabled = False

        elif self.local_obstacle_point_click_enabled:
        
            # Store the relative position
            self.dots.append((dot_relative_x, dot_relative_y))

            # Send coordinates to backend algorithm
            self.save_local_obstacle_to_file(relative_x, relative_y)

            # Trigger a repaint of the widget
            self.update()

    def save_start_point_to_file(self, relative_x, relative_y, filename='start_point.txt'):
        """Save the clicked point's coordinates to a file."""
        with open(filename, 'w') as file:
            file.write(f"[{relative_x}, {relative_y}]\n")
        print(f"Start point saved to {filename}")

    def save_end_point_to_file(self, relative_x, relative_y, filename='end_point.txt'):
        """Save the clicked point's coordinates to a file."""
        with open(filename, 'w') as file:
            file.write(f"[{relative_x}, {relative_y}]\n")
        print(f"End point saved to {filename}")

    def save_local_obstacle_to_file(self, relative_x, relative_y, filename='local_obstacles.txt'):
        with open(filename, 'a') as file:
            # Write the inputs to the file, each on a new line
            file.write(f"[{relative_x}, {relative_y}]\n")
        print(f"Data saved to {filename}")

    def on_backend_result(self, result):
        """Handle the result from the backend worker."""
        print(result)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        # Draw the background image if loaded
        if self.background_image:
            painter.drawPixmap(0, 0, self.width(), self.height(), self.background_image)
        else:
            # If no map is selected, display a placeholder
            painter.setBrush(QBrush(QColor(240, 240, 240)))  # Light gray background
            painter.drawRect(0, 0, self.width(), self.height())
            painter.setPen(QColor(150, 150, 150))  # Gray color for the text
            painter.setFont(QFont("Arial", 16))
            painter.drawText(self.rect(), QtCore.Qt.AlignCenter, "Please select a map and refer to the terminal for instructions.")

        # Recalculate the dots' positions based on the current size of the map
        map_width = self.width()
        map_height = self.height()

        painter.setBrush(QBrush(QColor(0, 0, 0)))  # Black color for the dots
        painter.setPen(QColor(0, 0, 0))  # Set text color to black

        for relative_x, relative_y in self.startpoint:
            x = int(relative_x * map_width * scx)
            y = int(relative_y * map_height * scy)
            painter.drawText((x - 5), (y - 5), 'Start')
        
        for relative_x, relative_y in self.endpoint:
            x = int(relative_x * map_width * scx)
            y = int(relative_y * map_height * scy)
            painter.drawText(x - 5, y - 5, 'End')
        
        painter.setPen(QColor(0, 0, 0, 0))  # Fully transparent pen
        #painter.setPen(QPen(QColor(255, 0, 0)))  # Red border (you can change the color)
        #painter.setPen(Qt.NoPen)  # Disable the pen to remove the border
        for relative_x, relative_y in self.dots:
            # Convert relative positions back to absolute positions based on the current size
            x = int(relative_x * map_width * scx)
            y = int(relative_y * map_height * scy)
            painter.drawEllipse(x - 5, y - 5, 10, 10)


class CustomizeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set properties for the embedded window
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtGui.QColor('white'))
        self.setPalette(palette)
        
        # Set widget size and position to cover the dropdown lists
        self.setGeometry(700, 30, 450, 350)

        # Add a label
        self.label_customersetting = QLabel("Customize Settings:", self)
        self.label_customersetting.setFont(font_title)
        self.label_customersetting.adjustSize()
        self.label_customersetting.move(20, 30)

        # Add a close button
        self.close_button = QPushButton("Close", self)
        self.close_button.setFont(font_button)
        self.close_button.setGeometry(175, 300, 100, 40)
        self.close_button.clicked.connect(self.hide)  # Hide the widget when close button is clicked

        self.setLine = QPushButton("Set Line", self)
        self.setLine.setFont(font_button)
        self.setLine.setGeometry(175, 100, 200, 40)

        self.setObstacles = QPushButton("Set Obstacles", self)
        self.setObstacles.setFont(font_button)
        self.setObstacles.setGeometry(155, 150, 200, 40)

        self.removal = QPushButton("Removal", self)
        self.removal.setFont(font_button)
        self.removal.setGeometry(175, 200, 200, 40)

        self.clear_all = QPushButton("Clear All", self)
        self.clear_all.setFont(font_button)
        self.clear_all.setGeometry(175, 250, 200, 40)

    def close_click(self):
        self.hide

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window properties
        self.setWindowTitle("Navigation System")
        self.setGeometry(400, 200, 1200, 700)
        self.setStyleSheet("background-color: #2C3E50;")

        self.original_width = 1200
        self.original_height = 700

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Command Label
        self.label_command = QLabel(self.central_widget)
        self.label_command.setText("Command:")
        self.label_command.setStyleSheet("color: #FFFFFF;")
        self.label_command.setFont(font_title)
        self.label_command.adjustSize()
        self.label_command.move(700, 30)

        # Command buttons
        self.btn_resume = QtWidgets.QPushButton("Resume", self.central_widget)
        self.btn_resume.setFont(font_button)
        self.btn_resume.setStyleSheet("""
            QPushButton {
                background-color: #5A85A9;  /* Muted blue background */
                color: white;               /* White text color */
                border: 2px solid #5A85A9;  /* Same color as background */
                border-radius: 15px;        /* Rounded corners */
                padding: 10px 20px;         /* Padding inside button */
                font-size: 16px;            /* Font size */
                font-weight: bold;          /* Make text bold */
            }

            QPushButton:hover {
                background-color: #B1CFEB;  /* Light pastel blue when hovered */
                border: 2px solid #B1CFEB;  /* Border matches hover color */
            }

            QPushButton:pressed {
                background-color: #4B6C7A;  /* Darker blue when pressed */
                border: 2px solid #4B6C7A;  /* Darker border when pressed */
            }
        """)
        self.btn_resume.move(700, 80)
        self.btn_resume.clicked.connect(self.resume)

        self.btn_pause = QtWidgets.QPushButton("Pause", self.central_widget)
        self.btn_pause.setFont(font_button)
        self.btn_pause.setStyleSheet("""
            QPushButton {
                background-color: #5A85A9;  /* Muted blue background */
                color: white;               /* White text color */
                border: 2px solid #5A85A9;  /* Same color as background */
                border-radius: 15px;        /* Rounded corners */
                padding: 10px 20px;         /* Padding inside button */
                font-size: 16px;            /* Font size */
                font-weight: bold;          /* Make text bold */
            }

            QPushButton:hover {
                background-color: #B1CFEB;  /* Light pastel blue when hovered */
                border: 2px solid #B1CFEB;  /* Border matches hover color */
            }

            QPushButton:pressed {
                background-color: #4B6C7A;  /* Darker blue when pressed */
                border: 2px solid #4B6C7A;  /* Darker border when pressed */
            }
        """)
        self.btn_pause.move(820, 80)
        self.btn_pause.clicked.connect(self.pause)

        # self.btn_manual = QtWidgets.QPushButton("Manual", self.central_widget)
        # self.btn_manual.setFont(font_button)
        # self.btn_manual.setStyleSheet("""
        #     QPushButton {
        #         background-color: #5A85A9;  /* Muted blue background */
        #         color: white;               /* White text color */
        #         border: 2px solid #5A85A9;  /* Same color as background */
        #         border-radius: 15px;        /* Rounded corners */
        #         padding: 10px 20px;         /* Padding inside button */
        #         font-size: 16px;            /* Font size */
        #         font-weight: bold;          /* Make text bold */
        #     }

        #     QPushButton:hover {
        #         background-color: #B1CFEB;  /* Light pastel blue when hovered */
        #         border: 2px solid #B1CFEB;  /* Border matches hover color */
        #     }

        #     QPushButton:pressed {
        #         background-color: #4B6C7A;  /* Darker blue when pressed */
        #         border: 2px solid #4B6C7A;  /* Darker border when pressed */
        #     }
        # """)
        # self.btn_manual.move(700, 110)

        self.btn_start = QtWidgets.QPushButton("Start", self.central_widget)
        self.btn_start.setFont(font_button)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #5A85A9;  /* Muted blue background */
                color: white;               /* White text color */
                border: 2px solid #5A85A9;  /* Same color as background */
                border-radius: 15px;        /* Rounded corners */
                padding: 10px 20px;         /* Padding inside button */
                font-size: 16px;            /* Font size */
                font-weight: bold;          /* Make text bold */
            }

            QPushButton:hover {
                background-color: #B1CFEB;  /* Light pastel blue when hovered */
                border: 2px solid #B1CFEB;  /* Border matches hover color */
            }

            QPushButton:pressed {
                background-color: #4B6C7A;  /* Darker blue when pressed */
                border: 2px solid #4B6C7A;  /* Darker border when pressed */
            }
        """)
        self.btn_start.move(820, 110)
        self.btn_start.clicked.connect(self.start)
    
        # # Joystick
        # self.joystick = Joystick(self.central_widget)
        # self.joystick.move(700, 160)

        #Map label
        self.label_map = QLabel(self.central_widget)
        self.label_map.setText("Map:")
        self.label_map.setFont(font_title)
        self.label_map.adjustSize()
        self.label_map.move(50, 30)
        self.label_map.setStyleSheet("color: #FFFFFF;")

        # Map selection
        self.map_select = QComboBox(self)
        self.map_select.setGeometry(980, 70, 150, 30)
        self.map_select.setStyleSheet("""
            QComboBox {
                background-color: #619196;  /* Muted blue background */
                color: white;               /* White text color */
                border: 2px solid #619196;  /* Border same as background */
                border-radius: 10px;        /* Rounded corners */
                padding: 5px 10px;          /* Padding inside the combo box */
                font-size: 16px;            /* Font size */
                font-weight: bold;          /* Make text bold */
            }

            QComboBox:hover {
                background-color: #A3BFD9;  /* Pastel light blue on hover */
                border: 2px solid #A3BFD9;  /* Border matches hover color */
            }

            QComboBox:pressed {
                background-color: #4C6D86;  /* Slightly darker blue when pressed */
                border: 2px solid #4C6D86;  /* Darker border when pressed */
            }

            QComboBox QAbstractItemView {
                background-color: #A3BFD9;  /* Light blue for dropdown */
                color: white;               /* White text in dropdown */
                border: 2px solid #5A85A9;  /* Border same as primary combo box color */
                border-radius: 5px;         /* Rounded corners for dropdown */
                selection-background-color: #4C6D86;  /* Darker blue when selecting */
                selection-color: white;     /* White text on selection */
            }

            QComboBox QAbstractItemView::item:hover {
                background-color: #A3BFD9;  /* Light blue on item hover */
                border: none;
            }
        """)

        self.label_map_select = QLabel("Map Select:", self)
        self.label_map_select.setFont(font_title)
        self.label_map_select.setStyleSheet("color: #FFFFFF;")
        self.label_map_select.setGeometry(980, 40, 150, 20)

        self.map_select.addItem("Select")
        self.map_select.addItem("Map 1")
        self.map_select.addItem("Map 2")
        self.map_select.addItem("Map 3")
        self.map_select.addItem("Map 4")
        self.map_select.addItem("Map 5")
        self.map_select.addItem("SG")
        self.map_select.addItem("NY")
        # self.map_select.addItem("Customize")
        self.map_select.currentIndexChanged.connect(self.map_changed)

        # Set ship size and shape
        self.label_shipsize = QLabel(self.central_widget)
        self.label_shipsize.setText("Ship size and shape:")
        self.label_shipsize.setStyleSheet("color: #FFFFFF;")
        self.label_shipsize.setFont(font_title)
        self.label_shipsize.adjustSize()
        self.label_shipsize.move(980, 120)

        self.ship_shape = QComboBox(self)
        self.ship_shape.setStyleSheet("""
            QComboBox {
                background-color: #619196;  /* Muted blue background */
                color: white;               /* White text color */
                border: 2px solid #619196;  /* Border same as background */
                border-radius: 10px;        /* Rounded corners */
                padding: 5px 10px;          /* Padding inside the combo box */
                font-size: 16px;            /* Font size */
                font-weight: bold;          /* Make text bold */
            }

            QComboBox:hover {
                background-color: #A3BFD9;  /* Pastel light blue on hover */
                border: 2px solid #A3BFD9;  /* Border matches hover color */
            }

            QComboBox:pressed {
                background-color: #4C6D86;  /* Slightly darker blue when pressed */
                border: 2px solid #4C6D86;  /* Darker border when pressed */
            }

            QComboBox QAbstractItemView {
                background-color: #A3BFD9;  /* Light blue for dropdown */
                color: white;               /* White text in dropdown */
                border: 2px solid #5A85A9;  /* Border same as primary combo box color */
                border-radius: 5px;         /* Rounded corners for dropdown */
                selection-background-color: #4C6D86;  /* Darker blue when selecting */
                selection-color: white;     /* White text on selection */
            }

            QComboBox QAbstractItemView::item:hover {
                background-color: #A3BFD9;  /* Light blue on item hover */
                border: none;
            }
        """)
        self.ship_shape.setGeometry(980, 155, 150, 30)

        self.ship_shape.addItem("Rectangle")
        self.ship_shape.addItem("Circle")

        self.label_length = QLabel(self.central_widget)
        self.label_length.setText("Length:")
        self.label_length.setFont(font_button)
        self.label_length.setStyleSheet("color: #FFFFFF;")
        self.label_length.move(980, 190)
        self.length_input = QLineEdit(self.central_widget)
        self.length_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;  /* White background */
                color: #333333;             /* Dark grey text color */
                border: 2px solid #D3D3D3;  /* Light grey border */
                border-radius: 10px;        /* Rounded corners */
                padding: 5px 10px;          /* Padding inside the text field */
                font-size: 16px;            /* Font size */
                font-weight: bold;          /* Make text bold */
            }

            QLineEdit:focus {
                border: 2px solid #5A85A9;  /* Soft blue border on focus */
                background-color: #f9f9f9;  /* Slightly off-white background on focus */
            }

            QLineEdit:hover {
                border: 2px solid #A0A0A0;  /* Darker grey border on hover */
            }

            QLineEdit::placeholder {
                color: #B0B0B0;             /* Light grey for placeholder text */
            }
        """)
        self.length_input.setGeometry(1040, 190, 100, 25)

        self.label_width = QLabel(self.central_widget)
        self.label_width.setText("Width:")
        self.label_width.setFont(font_button)
        self.label_width.setStyleSheet("color: #FFFFFF;")
        self.label_width.move(980, 220)
        self.width_input = QLineEdit(self.central_widget)
        self.width_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;  /* White background */
                color: #333333;             /* Dark grey text color */
                border: 2px solid #D3D3D3;  /* Light grey border */
                border-radius: 10px;        /* Rounded corners */
                padding: 5px 10px;          /* Padding inside the text field */
                font-size: 16px;            /* Font size */
                font-weight: bold;          /* Make text bold */
            }

            QLineEdit:focus {
                border: 2px solid #5A85A9;  /* Soft blue border on focus */
                background-color: #f9f9f9;  /* Slightly off-white background on focus */
            }

            QLineEdit:hover {
                border: 2px solid #A0A0A0;  /* Darker grey border on hover */
            }

            QLineEdit::placeholder {
                color: #B0B0B0;             /* Light grey for placeholder text */
            }
        """)
        self.width_input.setGeometry(1040, 220, 100, 25)

        self.label_radius = QLabel(self.central_widget)
        self.label_radius.setText("Radius:")
        self.label_radius.setFont(font_button)
        self.label_radius.setStyleSheet("color: #FFFFFF;")
        self.label_radius.move(980, 210)
        self.radius_input = QLineEdit(self.central_widget)
        self.radius_input.setGeometry(1040, 210, 100, 25)
        self.radius_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;  /* White background */
                color: #333333;             /* Dark grey text color */
                border: 2px solid #D3D3D3;  /* Light grey border */
                border-radius: 10px;        /* Rounded corners */
                padding: 5px 10px;          /* Padding inside the text field */
                font-size: 16px;            /* Font size */
                font-weight: bold;          /* Make text bold */
            }

            QLineEdit:focus {
                border: 2px solid #5A85A9;  /* Soft blue border on focus */
                background-color: #f9f9f9;  /* Slightly off-white background on focus */
            }

            QLineEdit:hover {
                border: 2px solid #A0A0A0;  /* Darker grey border on hover */
            }

            QLineEdit::placeholder {
                color: #B0B0B0;             /* Light grey for placeholder text */
            }
        """)
        self.label_radius.hide()
        self.radius_input.hide()
        self.ship_shape.currentIndexChanged.connect(self.toggle_input_fields)

        self.btn_setship = QtWidgets.QPushButton("Set", self.central_widget)
        self.btn_setship.setFont(font_button)
        self.btn_setship.setStyleSheet("""
            QPushButton {
                background-color: #E5AAA4;  /* Soft peachy-pink background */
                color: white;               /* White text color */
                border: 2px solid #e5AAA4;  /* Border same as background */
                border-radius: 15px;        /* Rounded corners */
                padding: 10px 20px;         /* Padding inside button */
                font-size: 16px;            /* Font size */
                font-weight: bold;          /* Make text bold */
            }

            QPushButton:hover {
                background-color: #B3D9D4;  /* Pastel mint green on hover */
                border: 2px solid #B3D9D4;  /* Border matches hover color */
            }

            QPushButton:pressed {
                background-color: #D9AFA0;  /* Muted darker peach when pressed */
                border: 2px solid #D9AFA0;  /* Darker border when pressed */
            }
        """)
        self.btn_setship.move(980, 250)
        self.btn_setship.clicked.connect(self.set)
        #self.btn_setship.clicked.connect(self.on_set_clicked)

        # Setting location
        self.label_locate = QLabel(self.central_widget)
        self.label_locate.setText("Locate:")
        self.label_locate.setStyleSheet("color: #FFFFFF;")
        self.label_locate.setFont(font_title)
        self.label_locate.adjustSize()
        self.label_locate.move(980, 300)

        self.btn_startpoint = QtWidgets.QPushButton("Start Point", self.central_widget)
        self.btn_startpoint.setFont(font_button)
        self.btn_startpoint.setStyleSheet("""
            QPushButton {
                background-color: #5A85A9;  /* Muted blue background */
                color: white;               /* White text color */
                border: 2px solid #5A85A9;  /* Same color as background */
                border-radius: 15px;        /* Rounded corners */
                padding: 10px 20px;         /* Padding inside button */
                font-size: 16px;            /* Font size */
                font-weight: bold;          /* Make text bold */
            }

            QPushButton:hover {
                background-color: #B1CFEB;  /* Light pastel blue when hovered */
                border: 2px solid #B1CFEB;  /* Border matches hover color */
            }

            QPushButton:pressed {
                background-color: #4B6C7A;  /* Darker blue when pressed */
                border: 2px solid #4B6C7A;  /* Darker border when pressed */
            }
        """)
        self.btn_startpoint.move(980, 330)
        self.btn_startpoint.clicked.connect(self.on_start_clicked)

        self.btn_endpoint = QtWidgets.QPushButton("End Point", self.central_widget)
        self.btn_endpoint.setFont(font_button)
        self.btn_endpoint.setStyleSheet("""
            QPushButton {
                background-color: #5A85A9;  /* Muted blue background */
                color: white;               /* White text color */
                border: 2px solid #5A85A9;  /* Same color as background */
                border-radius: 15px;        /* Rounded corners */
                padding: 10px 20px;         /* Padding inside button */
                font-size: 16px;            /* Font size */
                font-weight: bold;          /* Make text bold */
            }

            QPushButton:hover {
                background-color: #B1CFEB;  /* Light pastel blue when hovered */
                border: 2px solid #B1CFEB;  /* Border matches hover color */
            }

            QPushButton:pressed {
                background-color: #4B6C7A;  /* Darker blue when pressed */
                border: 2px solid #4B6C7A;  /* Darker border when pressed */
            }
        """)
        self.btn_endpoint.move(980, 360)
        self.btn_endpoint.clicked.connect(self.on_end_clicked)

        # Map
        self.map = Map(self.central_widget)


        self.label_sensor_data = QLabel(self.central_widget)
        self.label_sensor_data.setText("Dashboard")
        self.label_sensor_data.setStyleSheet("color: #FFFFFF;")
        self.label_sensor_data.setFont(font_title)
        self.label_sensor_data.adjustSize()
        self.label_sensor_data.move(700, 160)
        #Sensor Data Window (Hidden Initially)
        self.sensor_data_window = QWidget(self)
        self.sensor_data_window.setStyleSheet("background-color: white; border: 1px solid black;")
        self.sensor_data_window.setGeometry(700, 195, 250, 185)
        self.sensor_data_label = QLabel("Sensor Data")
        self.sensor_data_window.show()
        # QTextEdit for displaying sensor data
        self.sensor_data_text_edit = QTextEdit(self.sensor_data_window)
        self.sensor_data_text_edit.setGeometry(10,10,230,165)
        self.sensor_data_text_edit.setReadOnly(True)
        self.sensor_data_text_edit.setStyleSheet("""
            QTextEdit {
                font-family: "Arial", sans-serif;  /* Set the font family */
                font-size: 16px;                   /* Set the font size */
                font-weight: normal;               /* Set the font weight (e.g., normal, bold) */
            }
        """)

        self.terminal_window = QTextEdit(self)
        self.terminal_window.setReadOnly(True)  # Make it read-only
        # Timer for updating sensor data
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sensor_data)
        #Terminal Window
        self.label_terminal = QLabel(self.central_widget)
        self.label_terminal.setText("Terminal")
        self.label_terminal.setFont(font_title)
        self.label_terminal.setStyleSheet("color: #FFFFFF;")
        self.label_terminal.adjustSize()
        self.label_terminal.move(700, 395)

        self.terminal_window.setReadOnly(True)  # Make it read-only
        self.terminal_window.setGeometry(700, 430, 450, 250) 
        self.terminal_window.setStyleSheet("background-color: white; border: 1px solid black;")

        # Redirect sys.stdout to the QTextEdit widget
        sys.stdout = RedirectedOutput(self.terminal_window)

        # QLabel to display the map image (initialize it here)
        self.map_image = QLabel(self.central_widget)
        self.map_image.setGeometry(50, 80, 600, 600)
        self.map_image.setStyleSheet("border: 1px solid black;")
        self.map_image.setScaledContents(True)  # To make the image scale properly
        self.map_image.hide()

        # Customize widget (hidden by default)
        self.customize_widget = CustomizeWidget(self.central_widget)
        self.customize_widget.hide()  # Initially hidden
        
        # Create a QProcess object
        self.process = QProcess(self)
        self.process.finished.connect(self.on_process_finished)
        
        self.image_list = []  # List to hold all the image paths
        self.image_index = 0  # To keep track of the current image index
        self.timer = QTimer(self)  # Timer for updating the images
        self.timer.timeout.connect(self.update_image)  # Call update_image every timeout
        
        self.paused = False
        self.sensor_data_window.show()  # Show the sensor data window
        self.sensor_data_text_edit.clear()  # Clear previous content
        self.update_sensor_data()  # Start the first reading

    #Update sensor data
    def update_sensor_data(self):
        try:
            # Clear the current contents of the QTextEdit
            self.sensor_data_text_edit.clear() 

            # Check if the file exists
            if not os.path.exists('sensor_data.txt'):
                self.sensor_data_text_edit.setPlainText("Sensor Data: The file does not exist.")
                print("The file does not exist.")
                print("Usage Instructions")
                print("Step 1: Please select a map.")
                print("Step 2: Please select the shape of the ship.")
                print("Step 3: Please select the ship's dimensions. ")
                print("Step 4: Please select a start point and end point.")
                print("Step 5: Once you are done with your selection, press set.")
                print("Step 6: Press the left mouse button to plot local obstacles. ")
                print("Step 7: Press start to run the program.")
                print("Step 8: Press pause to pause the program.")
                print("Step 9: Press resume to continue running the program.")
                return
            
            with open('sensor_data.txt', 'r') as file:
                content = file.read().strip()  # Read and strip whitespace
                
                if content:
                    self.sensor_data_text_edit.setPlainText(content)  # Display content
                else:
                    self.sensor_data_text_edit.setPlainText("Sensor Data: No data available.")
        
        except FileNotFoundError:
            self.sensor_data_text_edit.setPlainText("Sensor Data: The file was not found.")
            print("The file was not found.")
        except IOError as e:
            self.sensor_data_text_edit.setPlainText("Sensor Data: Error reading data.")
            print(f"IO Error reading sensor data: {e}")
        except Exception as e:
            self.sensor_data_text_edit.setPlainText("Sensor Data: An unexpected error occurred.")
            print(f"Unexpected error reading sensor data: {e}")

        # Schedule the next call to this method
        QtCore.QTimer.singleShot(500, self.update_sensor_data)  # Call

    def map_changed(self):
        selected_map = self.map_select.currentText()

        if selected_map == "Map 1":
            self.map.load_background_image("Images/Map_1.png")
        elif selected_map == "Map 2":
            self.map.load_background_image("Images/Map_2.png")
        elif selected_map == "Map 3":
            self.map.load_background_image("Images/Map_3.png")
        elif selected_map == "Map 4":
            self.map.load_background_image("Images/Map_4.png")
        elif selected_map == "Map 5":
            self.map.load_background_image("Images/Map_5.png")
        elif selected_map == "SG":
            self.map.load_background_image("Images/SG.png") #Why doesn't A*Star search harder, when I put start coordinates as 5, 40, it doesn't see a path
        elif selected_map == "NY":
            self.map.load_background_image("Images/NY.png")
        elif selected_map == "Customize":
            self.show_customize_widget()
            self.map_select.lower()
            self.ship_shape.lower()
        elif selected_map == "Select": 
            self.map_image.clear()
            self.map.background_image = None
            self.update()
            

    # Add this method to display the image in the QLabel for the map
    def display_map_image(self, image_path): # Aaryan
         # Clear the existing pixmap before setting a new one
        self.map_image.clear()
        
        # Load the new image and set it as the pixmap
        pixmap = QPixmap(image_path)
        self.map_image.setPixmap(pixmap)

        # Force the label to update its display
        self.map_image.repaint()

    def toggle_input_fields(self):
        if self.ship_shape.currentText() == "Circle":
            self.label_length.hide()
            self.length_input.hide()
            self.label_width.hide()
            self.width_input.hide()
            self.label_radius.show()
            self.radius_input.show()
        else:
            self.label_length.show()
            self.length_input.show()
            self.label_width.show()
            self.width_input.show()
            self.label_radius.hide()
            self.radius_input.hide()

    def show_customize_widget(self):
        self.customize_widget.show()
        self.customize_widget.raise_()

    def resizeEvent(self, event):
        new_width = self.width()
        new_height = self.height()

        # Calculate scale factors
        scale_x = new_width / self.original_width
        scale_y = new_height / self.original_height
        global scx
        global scy
        scx = scale_x
        scy = scale_y
        
        # Scale and move widgets proportionally
        self.label_command.move(int(700 * scale_x), int(30 * scale_y))
        self.label_map.move(int(50 * scale_x), int(30 * scale_y))
        self.btn_resume.setGeometry(int(700 * scale_x), int(68 * scale_y),int(82 * scale_x), int(40 * scale_y) )
        self.btn_pause.setGeometry(int(784 * scale_x), int(68 * scale_y),int(82 * scale_x), int(40 * scale_y) )
        # self.btn_manual.setGeometry(int(700 * scale_x), int(121 * scale_y),int(120 * scale_x), int(40 * scale_y) )
        self.btn_start.setGeometry(int(868 * scale_x), int(68 * scale_y),int(82 * scale_x), int(40 * scale_y) )
        # self.resizeJoystick(scale_x, scale_y)

        self.label_locate.move(int(980 * scale_x), int(255 * scale_y))
        self.btn_startpoint.setGeometry(int(980 * scale_x), int(293 * scale_y), int(170 * scale_x), int(40 * scale_y))
        self.btn_endpoint.setGeometry(int(980 * scale_x), int(334 * scale_y), int(170 * scale_x), int(40 * scale_y))
        self.btn_setship.setGeometry(int(980 * scale_x), int(378 * scale_y), int(170 * scale_x), int(40 * scale_y))
        self.map.setGeometry(int(50 * scale_x), int(70 * scale_y), int(600 * scale_x), int(600 * scale_y))
        self.map_select.setGeometry(int(980 * scale_x), int(68 * scale_y), int(170 * scale_x), int(30 * scale_y))
        self.label_sensor_data.move(int(700 * scale_x), int(395*scale_y))
        # In your resizeEvent method, add the following for label_map_select
        self.label_map_select.setGeometry(int(980 * scale_x), int(30 * scale_y), int(150 * scale_x), int(30 * scale_y))

        self.label_shipsize.move(int(980 * scale_x), int(114 * scale_y))
        self.ship_shape.setGeometry(int(980 * scale_x), int(150 * scale_y), int(170 * scale_x), int(30 * scale_y))
        self.label_length.move(int(980 * scale_x), int(190 * scale_y))
        self.label_width.move(int(980 * scale_x), int(220 * scale_y))
        self.label_radius.move(int(980 * scale_x), int(215 * scale_y))
        self.length_input.setGeometry(int(1040 * scale_x), int(185 * scale_y), int(110 * scale_x), int(25 * scale_y))
        self.width_input.setGeometry(int(1040 * scale_x), int(215 * scale_y), int(110 * scale_x), int(25 * scale_y))
        self.radius_input.setGeometry(int(1040 * scale_x), int(210 * scale_y), int(110 * scale_x), int(25 * scale_y))
       

        #scaling for customize widget window
        self.customize_widget.setGeometry(int(700*scale_x), int(30*scale_y), int(450*scale_x), int(350*scale_y))
        self.customize_widget.close_button.setGeometry(int(350*scale_x), int(290*scale_y), int(100*scale_x), int(40*scale_y))
        self.customize_widget.setLine.setGeometry(int(135*scale_x), int(100*scale_y), int(200*scale_x), int(40*scale_y))
        self.customize_widget.setObstacles.setGeometry(int(135*scale_x), int(150*scale_y), int(200*scale_x), int(40*scale_y))
        self.customize_widget.removal.setGeometry(int(135*scale_x), int(200*scale_y), int(200*scale_x), int(40*scale_y))
        self.customize_widget.clear_all.setGeometry(int(135*scale_x), int(250*scale_y), int(200*scale_x), int(40*scale_y))
        
        # Adjust window size
        self.sensor_data_window.setGeometry(int(700 * scale_x), int(166 * scale_y), int(250 * scale_x), int(206 * scale_y))
        self.sensor_data_text_edit.setGeometry(int(10 * scale_x), int(10 * scale_y), int(230 * scale_x), int(186 * scale_y))
        self.label_sensor_data.move(int(700 * scale_x), int(128*scale_y))
        self.terminal_window.setGeometry(int(700 * scale_x), int(426 * scale_y), int(450 * scale_x), int(244 * scale_y))
        self.label_terminal.move(int(700 * scale_x), int(388 * scale_y))
        #return scx, scy


    def load_images(self):
        figs_folder = 'figs'  # Change this to your actual path
        self.image_list = sorted([os.path.join(figs_folder, img) for img in os.listdir(figs_folder) 
                              if img.startswith('frame_') and img.endswith('.png')],
                             key=lambda x: int(re.findall(r'\d+', os.path.basename(x))[0]))


        if self.image_list:
            QTimer.singleShot(1000, self.start_image_update)   # Start the timer with a 1-second interval              
            
    def run_subprocess(self, command):
        # if os.name == 'nt':
            # startupinfo = subprocess.STARTUPINFO()
            # startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.process = subprocess.Popen(['python'] + command)

    def closeEvent(self, event):
        self.process.kill()
        
    def set(self): #Anything changed in this GUI script after we press "set" will not be changed because of the subprocess (matplotlib) running takes over all of the computing power
        print("Set button clicked.")
        self.map.local_obstacle_click_enabled.emit()  # Emit the signal to enable map clicks
    
        try:
            selected_map = self.map_select.currentText()
        
            
            if self.ship_shape.currentText() == "Circle":
                radius = float(self.radius_input.text())
                command = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'test_dwa_astar_v5.py'), str(radius), selected_map]
            elif self.ship_shape.currentText() == "Rectangle":
                length = float(self.length_input.text())
                width = float(self.width_input.text())
                command = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'test_dwa_astar_v5.py'), str(length), str(width), selected_map]         

            self.run_subprocess(command)
            # Start the 5 seconds delay
            QTimer.singleShot(5000, self.load_images)
            
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numbers.")
            
    def start_image_update(self):
        # Start the main timer with a 3 second interval
        self.timer.start(3000)
    
    
    def update_image(self):
        # Check if we have a valid image list
        if self.image_list:
            # If the index is within the bounds of the image list, load the next image
            if self.image_index < len(self.image_list):
                image_path = self.image_list[self.image_index]
                print("Loading: ", image_path)

                # Load the image as QImage
                image = QImage(image_path)
                
                if self.map_select.currentText() == "NY" or self.map_select.currentText() == "SG":
                    crop_top = 15
                    crop_bottom = 15
                    crop_left = 17
                    crop_right = 17
                else:
                    crop_top = 50
                    crop_bottom = 50
                    crop_left = 50
                    crop_right = 50

                # Calculate new dimensions after cropping
                original_width = image.width()
                original_height = image.height()
                new_width = original_width - crop_left - crop_right
                new_height = original_height - crop_top - crop_bottom

                # Create the cropping rectangle
                crop_rect = QRect(crop_left, crop_top, new_width, new_height)

                # Crop the image
                cropped_image = image.copy(crop_rect)

                # Use the map's load_background_image function with the resized image
                self.map.load_background_image(QPixmap.fromImage(cropped_image))  # Load the resized image

                self.image_index += 1  # Move to the next image
            else:
                # We've reached the end of the current list, try reloading
                previous_image_index = self.image_index  # Store the current index
                self.load_images()
                

                if len(self.image_list) > previous_image_index:  
                    # If new images are found, continue from the last index
                    self.image_index = previous_image_index
                    if not self.paused:
                        self.update_image()  # Call update_image to load the next image
                else:
                    # If no new images are found, stop updating
                    self.timer.stop()
        else:
            # No images in the list initially, stop the timer
            self.timer.stop()
    
    def resume(self):
        if self.paused:
            self.paused = False  # Resume if paused
            print("Resuming")
        
        #self.image_index = 0  # Initialize the index
        self.timer.start(500)  # Start the timer with the interval

    
    def pause(self):
        if not self.paused:  # Only pause if not already paused
            self.paused = True  # Set the paused flag
            print("Pausing")
            self.timer.stop()  # Stop the timer to prevent further calls
        else:
            print("Already paused")

    def start(self):
        print("Pressed Start")
        with open('local_obstacles.txt', 'a') as file:
        # Write "resume" followed by a newline character
            file.write("resume\n")
    
    def on_process_finished(self):
            # Handle the completion of the process
            result = self.process.readAllStandardOutput().data().decode()
            error = self.process.readAllStandardError().data().decode()

            if self.process.exitCode() != 0:
                QMessageBox.warning(self, "Error", f"Script error: {error}")
            else:
                QMessageBox.information(self, "Success", result)

    def on_start_clicked(self):
        """Trigger the signal to allow map clicks."""
        print("Start Point button clicked.")
        self.map.start_click_enabled.emit()  # Emit the signal to enable map clicks

    def on_end_clicked(self):
        """Trigger the signal to allow map clicks."""
        print("End Point button clicked.")
        self.map.end_click_enabled.emit()  # Emit the signal to enable map clicks
        
    def closeEvent(self, event):
        # Ensure there is a subprocess and it is still active
        if hasattr(self, 'process') and self.process is not None:
            # Try to terminate the process gracefully
            self.process.terminate()
            try:
                # Wait briefly for the process to terminate
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                # If the process does not terminate, force kill it
                print("Process did not terminate in time; forcing kill.")
                self.process.kill()
                self.process.wait()  # Ensure it is fully terminated after killing

        # Reset stdout to its original state
        sys.stdout = sys.__stdout__
        
        # Call the base class closeEvent to ensure the window closes properly
        super().closeEvent(event)



            
def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
