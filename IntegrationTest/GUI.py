from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QComboBox, QPushButton, QLineEdit, QMessageBox, QRadioButton, QHBoxLayout, QButtonGroup
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QImage
from PyQt5.QtCore import QThread, pyqtSignal, QProcess, QTimer, QRect
import sys
import math
import subprocess
import os
import time
import re

font_title = QFont('Athelas', 16)
font_title.setBold(True)

font_button = QFont('Athelas', 12)

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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: white; border: 2px solid black; padding: 1px;")
        self.setGeometry(50, 80, 600, 570)
        self.dots = []  # List to store dots as relative positions (percentage of the width and height)
        self.background_image = None

    def load_background_image(self, image_path):
        self.background_image = QPixmap(image_path)
        self.update()

    # def clear_file(self, filename='local_obstacles.txt'):
    #     # Open the file in write mode to clear its contents
    #     with open(filename, 'w') as file:
    #         file.write('')  # Clear the file by writing an empty string
    #     print(f"File {filename} cleared.")

    def mousePressEvent(self, event):
        # Get the current size of the map
        map_width = self.width()
        map_height = self.height()

        # # Calculate the relative position as a percentage of the map size
        dot_relative_x = event.x() / map_width
        dot_relative_y = event.y() / map_height
        
        relative_x = event.x()/10
        relative_y = (map_height - event.y())/10


        # Store the relative position
        self.dots.append((dot_relative_x, dot_relative_y))

        # Send coordinates to backend algorithm
        #self.send_coordinates_to_backend(relative_x, relative_y)
        self.add_coordinates_to_file(relative_x, relative_y)

        # Trigger a repaint of the widget
        self.update()

    def add_coordinates_to_file(self, relative_x, relative_y, filename='local_obstacles.txt'):
        with open(filename, 'a') as file:
            # Write the inputs to the file, each on a new line
            file.write(f"[{relative_x}, {relative_y}]\n")
        print(f"Data saved to {filename}")

    # def send_coordinates_to_backend(self, relative_x, relative_y):
    # #Send the clicked coordinates to the backend algorithm using QThread to avoid blocking the GUI.
    #     try:
    #         # Convert relative coordinates to absolute positions based on the map size
    #         map_width = self.width()
    #         map_height = self.height()
    #         abs_x = int(relative_x * map_width)
    #         abs_y = int(relative_y * map_height)

    #         print(f"Sending coordinates to backend: {abs_x}, {abs_y}")

    #         # Run the backend in a separate thread to avoid blocking the GUI
    #         self.worker_thread = BackendWorker(abs_x, abs_y)
    #         self.worker_thread.result_ready.connect(self.on_backend_result)
    #         self.worker_thread.resume()

    #     except Exception as e:
    #         print(f"Error sending coordinates to backend: {e}")

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
            painter.drawText(self.rect(), QtCore.Qt.AlignCenter, "Please select a map")

        # Recalculate the dots' positions based on the current size of the map
        map_width = self.width()
        map_height = self.height()

        painter.setBrush(QBrush(QColor(0, 0, 0)))  # Black color for the dots
        for relative_x, relative_y in self.dots:
            # Convert relative positions back to absolute positions based on the current size
            x = int(relative_x * map_width)
            y = int(relative_y * map_height)
            painter.drawEllipse(x - 5, y - 5, 10, 10)

class Joystick(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set joystick properties
        self.joystick_radius = 25
        self.joystick_position = [100, 100]  # Starting position of the joystick (center of the widget)
        self.circle_radius = 100  # Radius of the circular joystick area
        self.setFixedSize(self.circle_radius * 2, self.circle_radius * 2)  # Size of the joystick area (diameter)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Draw circular background (joystick area)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(220, 220, 220)))
        painter.drawEllipse(0, 0, self.circle_radius * 2, self.circle_radius * 2)

        # Draw the joystick (movable circle) with integer values
        painter.setBrush(QtGui.QBrush(QtGui.QColor(50, 50, 250)))
        painter.drawEllipse(int(self.joystick_position[0] - self.joystick_radius),
                            int(self.joystick_position[1] - self.joystick_radius),
                            int(self.joystick_radius * 2),
                            int(self.joystick_radius * 2))

    def mouseMoveEvent(self, event):
        # Get the current mouse position relative to the widget
        x = event.x()
        y = event.y()

        # Calculate the distance from the center of the circle (circle_radius, circle_radius)
        distance = math.sqrt((x - self.circle_radius) ** 2 + (y - self.circle_radius) ** 2)

        # If the distance is within the circle radius, update the joystick position
        if distance <= self.circle_radius - self.joystick_radius:
            self.joystick_position = [x, y]
        else:
            # Restrict movement to the edge of the circle
            angle = math.atan2(y - self.circle_radius, x - self.circle_radius)
            self.joystick_position = [
                self.circle_radius + (self.circle_radius - self.joystick_radius) * math.cos(angle),
                self.circle_radius + (self.circle_radius - self.joystick_radius) * math.sin(angle)
            ]

        self.update()  # Trigger paintEvent to redraw the joystick

    def mouseReleaseEvent(self, event):
        # Return the joystick to the center when the mouse is released
        self.joystick_position = [self.circle_radius, self.circle_radius]
        self.update()


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

        self.original_width = 1200
        self.original_height = 700

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Code used for testing only !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.resume_label = QLabel(self.central_widget)
        self.resume_label.setText("Resume-:")
        self.resume_label.move(200, 30)
        self.resume_x_edit = QLineEdit(self.central_widget)
        self.resume_x_edit.setGeometry(250, 30, 50, 25)
        self.resume_y_edit = QLineEdit(self.central_widget)
        self.resume_y_edit.setGeometry(300, 30, 50, 25)

        self.end_label = QLabel(self.central_widget)
        self.end_label.setText("End-:")
        self.end_label.move(400, 30)
        self.end_x_edit = QLineEdit(self.central_widget)
        self.end_x_edit.setGeometry(450, 30, 50, 25)
        self.end_y_edit = QLineEdit(self.central_widget)
        self.end_y_edit.setGeometry(500, 30, 50, 25)

        # Command Label
        self.label_command = QLabel(self.central_widget)
        self.label_command.setText("Command:")
        self.label_command.setFont(font_title)
        self.label_command.adjustSize()
        self.label_command.move(700, 30)

        # Command buttons
        self.btn_resume = QtWidgets.QPushButton("Resume", self.central_widget)
        self.btn_resume.setFont(font_button)
        self.btn_resume.move(700, 70)
        self.btn_resume.clicked.connect(self.resume)

        self.btn_pause = QtWidgets.QPushButton("Pause", self.central_widget)
        self.btn_pause.setFont(font_button)
        self.btn_pause.move(820, 70)
        self.btn_pause.clicked.connect(self.pause)

        self.btn_manual = QtWidgets.QPushButton("Manual", self.central_widget)
        self.btn_manual.setFont(font_button)
        self.btn_manual.move(700, 110)

        self.btn_start = QtWidgets.QPushButton("Start", self.central_widget)
        self.btn_start.setFont(font_button)
        self.btn_start.move(820, 110)
        self.btn_start.clicked.connect(self.start)

        # Joystick
        self.joystick = Joystick(self.central_widget)
        self.joystick.move(700, 160)

        #Map label
        self.label_map = QLabel(self.central_widget)
        self.label_map.setText("Map:")
        self.label_map.setFont(font_title)
        self.label_map.adjustSize()
        self.label_map.move(50, 30)

        # Map selection
        self.map_select = QComboBox(self)
        self.map_select.setGeometry(1000, 70, 150, 30)

        self.map_select.addItem("Select")
        self.map_select.addItem("Map 1")
        self.map_select.addItem("Map 2")
        self.map_select.addItem("Map 3")
        self.map_select.addItem("Map 4")
        self.map_select.addItem("Map 5")
        self.map_select.addItem("SG")
        self.map_select.addItem("NY")
        self.map_select.addItem("Customize")
        self.map_select.currentIndexChanged.connect(self.map_changed)

        # Set ship size and shape
        self.label_shipsize = QLabel(self.central_widget)
        self.label_shipsize.setText("Ship size:")
        self.label_shipsize.setFont(font_title)
        self.label_shipsize.adjustSize()
        self.label_shipsize.move(980, 120)

        self.ship_shape = QComboBox(self)
        self.ship_shape.setGeometry(980, 155, 150, 30)

        self.ship_shape.addItem("Rectangle")
        self.ship_shape.addItem("Circle")

        self.label_length = QLabel(self.central_widget)
        self.label_length.setText("Length:")
        self.label_length.move(980, 190)
        self.length_input = QLineEdit(self.central_widget)
        self.length_input.setGeometry(1040, 190, 100, 25)

        self.label_width = QLabel(self.central_widget)
        self.label_width.setText("Width:")
        self.label_width.move(980, 220)
        self.width_input = QLineEdit(self.central_widget)
        self.width_input.setGeometry(1040, 220, 100, 25)

        self.label_radius = QLabel(self.central_widget)
        self.label_radius.setText("Radius:")
        self.label_radius.move(980, 190)
        self.radius_input = QLineEdit(self.central_widget)
        self.radius_input.setGeometry(1040, 190, 100, 25)
        self.label_radius.hide()
        self.radius_input.hide()
        self.ship_shape.currentIndexChanged.connect(self.toggle_input_fields)

        self.btn_setship = QtWidgets.QPushButton("Set", self.central_widget)
        self.btn_setship.setFont(font_button)
        self.btn_setship.move(980, 250)
        self.btn_setship.clicked.connect(self.set)

        # Setting location
        self.label_locate = QLabel(self.central_widget)
        self.label_locate.setText("Locate:")
        self.label_locate.setFont(font_title)
        self.label_locate.adjustSize()
        self.label_locate.move(980, 300)

        self.btn_startpoint = QtWidgets.QPushButton("Start Point", self.central_widget)
        self.btn_startpoint.setFont(font_button)
        self.btn_startpoint.move(980, 330)

        self.btn_endpoint = QtWidgets.QPushButton("End Point", self.central_widget)
        self.btn_endpoint.setFont(font_button)
        self.btn_endpoint.move(980, 360)

        # Map
        self.map = Map(self.central_widget)

        # Buttons for additional windows
        self.btn_dashboard = QtWidgets.QPushButton("Dashboard", self.central_widget)
        self.btn_dashboard.setFont(font_button)
        self.btn_dashboard.move(700, 400)

        self.btn_notification = QtWidgets.QPushButton("Notification", self.central_widget)
        self.btn_notification.setFont(font_button)
        self.btn_notification.move(800, 400)

        self.btn_sensor_data = QtWidgets.QPushButton("Sensor data", self.central_widget)
        self.btn_sensor_data.setFont(font_button)
        self.btn_sensor_data.move(930, 400)

        # Create unique windows for each button
        self.dashboard_window = QWidget(self)
        self.dashboard_window.setStyleSheet("background-color: white; border: 1px solid black;")
        self.dashboard_window.setGeometry(700, 430, 450, 220)
        self.dashboard_label = QLabel("Dashboard", self.dashboard_window)
        self.dashboard_label.move(10, 10)

        self.notification_window = QWidget(self)
        self.notification_window.setStyleSheet("background-color: white; border: 1px solid black;")
        self.notification_window.setGeometry(700, 430, 450, 220)
        self.notification_label = QLabel("Notifications", self.notification_window)
        self.notification_label.move(10, 10)

        self.sensor_data_window = QWidget(self)
        self.sensor_data_window.setStyleSheet("background-color: white; border: 1px solid black;")
        self.sensor_data_window.setGeometry(700, 430, 450, 220)
        self.sensor_data_label = QLabel("Sensor Data", self.sensor_data_window)
        self.sensor_data_label.move(10, 10)

        # Initially hide all the windows
        self.notification_window.hide()
        self.sensor_data_window.hide()

        # Connect button clicks to show the corresponding window
        self.btn_dashboard.clicked.connect(lambda: self.show_window(self.dashboard_window))
        self.btn_notification.clicked.connect(lambda: self.show_window(self.notification_window))
        self.btn_sensor_data.clicked.connect(lambda: self.show_window(self.sensor_data_window))
        
        # QLabel to display the map image (initialize it here)
        self.map_image = QLabel(self.central_widget)
        self.map_image.setGeometry(50, 80, 600, 570)
        self.map_image.setStyleSheet("border: 1px solid black;")
        self.map_image.setScaledContents(True)  # To make the image scale properly
        self.map_image.hide() #Testing!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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

    def show_window(self, window):
        self.dashboard_window.hide()
        self.notification_window.hide()
        self.sensor_data_window.hide()

        # Show the selected window
        window.show()


    def map_changed(self):
        selected_map = self.map_select.currentText()
        file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'Images',selected_map.replace(" ", "_")+".png")

        if selected_map == "Customize":
            self.show_customize_widget()
            self.map_select.lower()
            self.ship_shape.lower()
        elif selected_map == "Select": 
            self.map_image.clear()
            self.map.background_image = None
            self.update()
        else: #Why doesn't A*Star search harder, when I put start coordinates as 5, 40, it doesn't see a path
            self.map.load_background_image(file_dir)
            

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

        # Scale and move widgets proportionally
        self.label_command.move(int(700 * scale_x), int(30 * scale_y))
        self.label_map.move(int(50 * scale_x), int(30 * scale_y))
        self.btn_resume.move(int(700 * scale_x), int(70 * scale_y))
        self.btn_pause.move(int(820 * scale_x), int(70 * scale_y))
        self.btn_manual.move(int(700 * scale_x), int(110 * scale_y))
        self.btn_start.move(int(820 * scale_x), int(110 * scale_y))
        self.joystick.move(int(700 * scale_x), int(160 * scale_y))
        self.label_locate.move(int(980 * scale_x), int(300 * scale_y))
        self.btn_startpoint.move(int(980 * scale_x), int(330 * scale_y))
        self.btn_endpoint.move(int(980 * scale_x), int(360 * scale_y))
        self.map.setGeometry(int(50 * scale_x), int(80 * scale_y), int(600 * scale_x), int(570 * scale_y))

        self.btn_dashboard.move(int(700 * scale_x), int(400 * scale_y))
        self.btn_notification.move(int(800 * scale_x), int(400 * scale_y))
        self.btn_sensor_data.move(int(930 * scale_x), int(400 * scale_y))

        self.map_select.setGeometry(int(1000 * scale_x), int(70 * scale_y), int(150 * scale_x), int(30 * scale_y))

        self.label_shipsize.move(int(980 * scale_x), int(120 * scale_y))
        self.ship_shape.setGeometry(int(980 * scale_x), int(155 * scale_y), int(150 * scale_x), int(30 * scale_y))
        self.label_length.move(int(980 * scale_x), int(190 * scale_y))
        self.label_width.move(int(980 * scale_x), int(220 * scale_y))
        self.label_radius.move(int(980 * scale_x), int(200 * scale_y))
        self.length_input.setGeometry(int(1040 * scale_x), int(190 * scale_y), int(100 * scale_x), int(25 * scale_y))
        self.width_input.setGeometry(int(1040 * scale_x), int(220 * scale_y), int(100 * scale_x), int(25 * scale_y))
        self.radius_input.setGeometry(int(1040 * scale_x), int(200 * scale_y), int(100 * scale_x), int(25 * scale_y))
        self.btn_setship.move(int(980 * scale_x), int(250 * scale_y))

        #scaling for customize widget window
        self.customize_widget.setGeometry(int(700*scale_x), int(30*scale_y), int(450*scale_x), int(350*scale_y))
        self.customize_widget.close_button.setGeometry(int(350*scale_x), int(290*scale_y), int(100*scale_x), int(40*scale_y))
        self.customize_widget.setLine.setGeometry(int(135*scale_x), int(100*scale_y), int(200*scale_x), int(40*scale_y))
        self.customize_widget.setObstacles.setGeometry(int(135*scale_x), int(150*scale_y), int(200*scale_x), int(40*scale_y))
        self.customize_widget.removal.setGeometry(int(135*scale_x), int(200*scale_y), int(200*scale_x), int(40*scale_y))
        self.customize_widget.clear_all.setGeometry(int(135*scale_x), int(250*scale_y), int(200*scale_x), int(40*scale_y))
        
        # Adjust window size
        for window in [self.dashboard_window, self.notification_window, self.sensor_data_window]:
            window.setGeometry(int(700 * scale_x), int(430 * scale_y), int(450 * scale_x), int(220 * scale_y))

    # def load_images(self):
    #     figs_folder = 'figs'  # Change this to your actual path
    #     self.image_list = sorted([os.path.join(figs_folder, img) for img in os.listdir(figs_folder) if img.startswith('frame_') and img.endswith('.png')])

    #     if self.image_list:
    #         QTimer.singleShot(1000, self.start_image_update)   # Start the timer with a 1-second interval
      
      
    def load_images(self):
        figs_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)),'figs')
        self.image_list = sorted([os.path.join(figs_folder, img) for img in os.listdir(figs_folder) 
                              if img.startswith('frame_') and img.endswith('.png')],
                             key=lambda x: int(re.findall(r'\d+', os.path.basename(x))[0]))


        if self.image_list:
            QTimer.singleShot(1000, self.start_image_update)   # Start the timer with a 1-second interval              
            
    def run_subprocess(self, command):
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.process = subprocess.Popen(['python'] + command, startupinfo=startupinfo)

    def closeEvent(self, event):
        self.process.kill()
        
    def set(self): #Anything changed in this GUI script after we press "set" will not be changed because of the subprocess (matplotlib) running takes over all of the computing power
        try:
            # Read coordinates from input fields
            resume_x = float(self.resume_x_edit.text())
            resume_y = float(self.resume_y_edit.text())
            end_x = float(self.end_x_edit.text())
            end_y = float(self.end_y_edit.text())
            selected_map = self.map_select.currentText()
        
            
            if self.ship_shape.currentText() == "Circle":
                radius = float(self.radius_input.text())
                command = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'test_dwa_astar_v5_2.py'), str(resume_x), str(resume_y), str(end_x), str(end_y), str(radius), selected_map]
            elif self.ship_shape.currentText() == "Rectangle":
                length = float(self.length_input.text())
                width = float(self.width_input.text())
                command = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'test_dwa_astar_v5_2.py', str(resume_x), str(resume_y), str(end_x), str(end_y), str(length), str(width), selected_map]
            
            # Start subprocess
            # self.process.start('python', command)   
            
            #Start subprocess in background without showing it
            # if os.name == 'nt':
            #     startupinfo = subprocess.STARTUPINFO()
            #     startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            #     self.process = subprocess.Popen(['python'] + command, startupinfo=startupinfo)             

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

                # # Define crop amounts
                # crop_top = 70
                # crop_bottom = 65
                # crop_left = 155
                # crop_right = 140
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
                #self.timer.start(1000) #Added a 1 second pause because there was occassionaly a scaling error where the image wasn't shown

                # Crop the image
                cropped_image = image.copy(crop_rect)

                # Resize the cropped image to desired dimensions (optional)
                #desired_width = 600  # Set your desired width after cropping
                #desired_height = 400  # Set your desired height after cropping
                #resized_image = cropped_image.scaled(desired_width, desired_height, QtCore.Qt.KeepAspectRatio)
                # resized_image = cropped_image.scaled(
                #     desired_width, 
                #     desired_height, 
                #     QtCore.Qt.KeepAspectRatio, 
                #     QtCore.Qt.SmoothTransformation
                # )

                # Use the map's load_background_image function with the resized image
                self.map.load_background_image(QPixmap.fromImage(cropped_image))  # Load the resized image
                #self.map.load_background_image(QPixmap.fromImage(resized_image))  # Load the resized image
                #self.map.load_background_image(QPixmap.fromImage(image))  # Load the image

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
    
    # def toggle_pause(self):
    #     if self.paused:
    #         self.resume()  # If paused, resume
    #     else:
    #         self.pause()  # If playing, pause
        
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
        with open('transition.txt', 'a') as file:
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
            
def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
