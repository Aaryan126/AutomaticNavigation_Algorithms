from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QComboBox, QPushButton, QLineEdit, QMessageBox, QRadioButton, QHBoxLayout, QButtonGroup
from PyQt5.QtGui import QFont, QPixmap
import sys
import math
import subprocess

font_title = QFont('Athelas', 16)
font_title.setBold(True)

font_button = QFont('Athelas', 12)


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
        self.start_label = QLabel(self.central_widget)
        self.start_label.setText("Start-:")
        self.start_label.move(200, 30)
        self.start_x_edit = QLineEdit(self.central_widget)
        self.start_x_edit.setGeometry(250, 30, 50, 25)
        self.start_y_edit = QLineEdit(self.central_widget)
        self.start_y_edit.setGeometry(300, 30, 50, 25)

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
        self.btn_start = QtWidgets.QPushButton("Start", self.central_widget)
        self.btn_start.setFont(font_button)
        self.btn_start.move(700, 70)

        self.btn_pause = QtWidgets.QPushButton("Pause", self.central_widget)
        self.btn_pause.setFont(font_button)
        self.btn_pause.move(820, 70)

        self.btn_manual = QtWidgets.QPushButton("Manual", self.central_widget)
        self.btn_manual.setFont(font_button)
        self.btn_manual.move(700, 110)

        self.btn_automatic = QtWidgets.QPushButton("Automatic", self.central_widget)
        self.btn_automatic.setFont(font_button)
        self.btn_automatic.move(820, 110)

        # Joystick
        self.joystick = Joystick(self.central_widget)
        self.joystick.move(700, 160)

        # Map selection
        self.map_select = QComboBox(self)
        self.map_select.setGeometry(1000, 70, 150, 30)

        self.map_select.addItem("Select")
        self.map_select.addItem("Map 1")
        self.map_select.addItem("Map 2")
        self.map_select.addItem("Map 3")
        self.map_select.addItem("Map 4")
        self.map_select.addItem("Map 5")
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
        self.label_map = QLabel(self.central_widget)
        self.label_map.setText("Map:")
        self.label_map.setFont(font_title)
        self.label_map.adjustSize()
        self.label_map.move(50, 30)

        self.map = QWidget(self.central_widget)
        self.map.setStyleSheet("background-color: white; border: 1px solid black;")
        self.map.setGeometry(50, 80, 600, 570)

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
        self.label_map_image = QLabel(self.central_widget)
        self.label_map_image.setGeometry(50, 80, 600, 570)
        self.label_map_image.setStyleSheet("border: 1px solid black;")
        self.label_map_image.setScaledContents(True)  # To make the image scale properly

        # Customize widget (hidden by default)
        self.customize_widget = CustomizeWidget(self.central_widget)
        self.customize_widget.hide()  # Initially hidden

    def show_window(self, window):
        # Hide all other windows
        self.dashboard_window.hide()
        self.notification_window.hide()
        self.sensor_data_window.hide()

        # Show the selected window
        window.show()

    #def map_changed(self):
    #    if self.map_select.currentText() == "Customize":
    #        self.show_customize_widget()
            
    # Add this method inside the MainWindow class
    
    def map_changed(self): #Aaryan
        selected_map = self.map_select.currentText()

        if selected_map == "Map 1":
            self.display_map_image("Images/1.png")
        elif selected_map == "Map 2":
            self.display_map_image("Images/2.png")
        elif selected_map == "Map 3":
            self.display_map_image("Images/3.png")
        elif selected_map == "Map 4":
            self.display_map_image("Images/4.png")
        elif selected_map == "Map 5":
            self.display_map_image("Images/5.png")
        elif selected_map == "Customize":
            self.show_customize_widget()

    # Add this method to display the image in the QLabel for the map
    def display_map_image(self, image_path): # Aaryan
         # Clear the existing pixmap before setting a new one
        self.label_map_image.clear()
        
        # Load the new image and set it as the pixmap
        pixmap = QPixmap(image_path)
        self.label_map_image.setPixmap(pixmap)

        # Force the label to update its display
        self.label_map_image.repaint()

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
        self.btn_start.move(int(700 * scale_x), int(70 * scale_y))
        self.btn_pause.move(int(820 * scale_x), int(70 * scale_y))
        self.btn_manual.move(int(700 * scale_x), int(110 * scale_y))
        self.btn_automatic.move(int(820 * scale_x), int(110 * scale_y))
        self.joystick.move(int(700 * scale_x), int(160 * scale_y))
        self.label_locate.move(int(980 * scale_x), int(300 * scale_y))
        self.btn_startpoint.move(int(980 * scale_x), int(330 * scale_y))
        self.btn_endpoint.move(int(980 * scale_x), int(360 * scale_y))
        self.label_map.move(int(50 * scale_x), int(30 * scale_y))
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


        # Adjust window size
        for window in [self.dashboard_window, self.notification_window, self.sensor_data_window]:
            window.setGeometry(int(700 * scale_x), int(430 * scale_y), int(450 * scale_x), int(220 * scale_y))


    def set(self):
        try:
            # Read coordinates from input fields
            start_x = float(self.start_x_edit.text())
            start_y = float(self.start_y_edit.text())
            end_x = float(self.end_x_edit.text())
            end_y = float(self.end_y_edit.text())
            
            selected_map = self.map_select.currentText()
            
            # result = subprocess.run(
            #          ['python', 'dwa_astar_v5.py', str(start_x), str(start_y), str(end_x), str(end_y)],
            #          capture_output=True, text=True
            #      )
            
            self.close()
            # Run the external script and capture the output
            #If Circle
            if self.ship_shape.currentText() == "Circle": 
                radius = float(self.radius_input.text())
                result = subprocess.run(
                    ['python', 'test_dwa_astar_v5.py', str(start_x), str(start_y), str(end_x), str(end_y), str(radius), selected_map],
                    capture_output=True, text=True
                )
            if self.ship_shape.currentText() == "Rectangle": 
                length = float(self.length_input.text())
                width = float(self.width_input.text())
                result = subprocess.run(
                    ['python', 'test_dwa_astar_v5.py', str(start_x), str(start_y), str(end_x), str(end_y), str(length), str(width), selected_map],
                    capture_output=True, text=True
                )
            
            # Check for errors
            if result.returncode != 0:
                QMessageBox.warning(self, "Error", f"Script error: {result.stderr.strip()}")
                return
            
            self.close()

            #Display the result
            #distance = result.stdout.strip()
            #QMessageBox.information(self, "Result", f"Calculated distance: {distance}")
            
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numbers.")

    
def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
