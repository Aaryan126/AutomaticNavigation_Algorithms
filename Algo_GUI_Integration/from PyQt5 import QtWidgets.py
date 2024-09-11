from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QComboBox
from PyQt5.QtGui import QFont
import sys

font_title = QFont('Athelas', 16)
font_title.setBold(True)

font_button = QFont('Athelas', 12)


class Joystick(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set joystick properties
        self.joystick_radius = 25
        self.center_position = [self.width() // 2, self.height() // 2]  # Center of the joystick
        self.setFixedSize(self.joystick_radius * 2, self.joystick_radius * 2)  # Size of the joystick area

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Draw background (joystick area)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(220, 220, 220)))
        painter.drawEllipse(0, 0, self.width(), self.height())  # Draw a circle

        # Draw the joystick (movable circle)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(50, 50, 250)))
        painter.drawEllipse(self.center_position[0] - self.joystick_radius,
                             self.center_position[1] - self.joystick_radius,
                             self.joystick_radius * 2, self.joystick_radius * 2)

    def mouseMoveEvent(self, event):
        # Handle joystick movement within circular boundaries
        x = event.x()
        y = event.y()

        # Calculate distance from the center
        distance_from_center = ((x - self.center_position[0])**2 + (y - self.center_position[1])**2)**0.5

        # Check if within joystick radius
        if distance_from_center <= self.joystick_radius:
            self.center_position = [x, y]
            self.update()  # Trigger paintEvent to redraw the joystick

    def mouseReleaseEvent(self, event):
        # Return the joystick to the center when the mouse is released
        self.center_position = [self.width() // 2, self.height() // 2]
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window properties
        self.setWindowTitle("Navigation System")
        self.setGeometry(400, 200, 1200, 700)

        # No central widget layout is used here. We use absolute positioning.
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

         #Command Label
        self.label_command = QtWidgets.QLabel(self.central_widget)
        self.label_command.setText("Command:")
        self.label_command.setFont(font_title)
        self.label_command.adjustSize()
        self.label_command.move(700, 30)

    #Command buttons
        self.btn_start = QtWidgets.QPushButton("Start", self.central_widget)
        self.btn_start.setFont(font_button)
        self.btn_start.move(700, 70) 
        #Function for start

        self.btn_pause = QtWidgets.QPushButton("Pause", self.central_widget)
        self.btn_pause.setFont(font_button)
        self.btn_pause.move(820, 70) 
        #Function for pause

        self.btn_manual = QtWidgets.QPushButton("Manual", self.central_widget)
        self.btn_manual.setFont(font_button)
        self.btn_manual.move(700, 110) 
        #Function for manual

        self.btn_automatic = QtWidgets.QPushButton("Automatic", self.central_widget)
        self.btn_automatic.setFont(font_button)
        self.btn_automatic.move(820, 110) 
        #Function for automatic

    #Joystick
        self.joystick = Joystick(self.central_widget)
        self.joystick.move(700, 160)  # Move joystick to desired position

    #Choose map
        self.map_select = QComboBox(self)
        self.map_select.setGeometry(1000, 70, 150, 30)  

        self.map_select.addItem("Map 1")
        self.map_select.addItem("Map 2")
        self.map_select.addItem("Map 3")
        self.map_select.addItem("Map 4")
        self.map_select.addItem("Map 5")
        self.map_select.addItem("Customize")

    #Ship size
        self.ship_select = QComboBox(self)
        self.ship_select.setGeometry(1000, 120, 150, 30)  

        self.ship_select.addItem("Small Ship")
        self.ship_select.addItem("Medium Ship")
        self.ship_select.addItem("Large Ship")

    #Velocity control
        self.label_control = QtWidgets.QLabel(self.central_widget)
        self.label_control.setText("Control:")
        self.label_control.setFont(font_title)
        self.label_control.adjustSize()
        self.label_control.move(980, 200)

        self.btn_accelerate = QtWidgets.QPushButton("Accelerate", self.central_widget)
        self.btn_accelerate.setFont(font_button)
        self.btn_accelerate.move(980, 240) 
        #Function for accelerate

        self.btn_decelerate = QtWidgets.QPushButton("Decelerate", self.central_widget)
        self.btn_decelerate.setFont(font_button)
        self.btn_decelerate.move(980, 280) 
        #Function for decelerate

    #Map
        self.label_map = QtWidgets.QLabel(self.central_widget)
        self.label_map.setText("Map:")
        self.label_map.setFont(font_title)
        self.label_map.adjustSize()
        self.label_map.move(50, 30)

        self.map = QWidget(self.central_widget)
        self.map.setStyleSheet("background-color: white; border: 1px solid black;")
        self.map.setGeometry(50, 80, 600, 570)

    #Dashboard
        self.btn_dashboard = QtWidgets.QPushButton("Dashboard", self.central_widget)
        self.btn_dashboard.setFont(font_button)
        self.btn_dashboard.move(700, 400) 
        #Function for dashboard

        self.btn_notification = QtWidgets.QPushButton("Notification", self.central_widget)
        self.btn_notification.setFont(font_button)
        self.btn_notification.move(800, 400) 
        #Function for notification

        self.btn_sensor_data = QtWidgets.QPushButton("Sensor data", self.central_widget)
        self.btn_sensor_data.setFont(font_button)
        self.btn_sensor_data.move(930, 400) 
        #Function for sensor data

        self.win_dashboard = QWidget(self.central_widget)
        self.win_dashboard.setStyleSheet("background-color: white; border: 1px solid black;")
        self.win_dashboard.setGeometry(700, 430, 450, 220)
        #Function for dashboard display

def window():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


window()

