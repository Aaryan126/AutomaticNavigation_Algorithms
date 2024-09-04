import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QRadioButton, QHBoxLayout, QButtonGroup

class RobotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.resize(400, 600)

        # Set the window title
        self.setWindowTitle("Robot Coordinate Input")

        # Create widgets
        self.start_label = QLabel("Start Coordinates")
        self.start_x_edit = QLineEdit()
        self.start_y_edit = QLineEdit()

        self.end_label = QLabel("End Coordinates")
        self.end_x_edit = QLineEdit()
        self.end_y_edit = QLineEdit()

         # Radio buttons for shape selection
        self.shape_label = QLabel("Select Robot Shape")
        self.circle_radio = QRadioButton("Circle")
        self.rectangle_radio = QRadioButton("Rectangle")
        self.rectangle_radio.setChecked(True)  # Default selection
        self.shape_group = QButtonGroup()
        self.shape_group.addButton(self.circle_radio)
        self.shape_group.addButton(self.rectangle_radio)

        # Dynamic input fields for dimensions
        self.length_label = QLabel("Length:")
        self.length_edit = QLineEdit()
        self.width_label = QLabel("Width:")
        self.width_edit = QLineEdit()
        self.radius_label = QLabel("Radius:")
        self.radius_edit = QLineEdit()
        self.radius_label.hide()
        self.radius_edit.hide()

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate)
        
        # Connect radio buttons to a method to toggle input fields
        self.circle_radio.toggled.connect(self.toggle_input_fields)

        # Layout
        shape_layout = QHBoxLayout()
        shape_layout.addWidget(self.circle_radio)
        shape_layout.addWidget(self.rectangle_radio)

        # Arrange widgets in a vertical layout
        layout = QVBoxLayout()
        layout.addWidget(self.start_label)
        layout.addWidget(QLabel("Start X:"))
        layout.addWidget(self.start_x_edit)
        layout.addWidget(QLabel("Start Y:"))
        layout.addWidget(self.start_y_edit)
        layout.addWidget(self.end_label)
        layout.addWidget(QLabel("End X:"))
        layout.addWidget(self.end_x_edit)
        layout.addWidget(QLabel("End Y:"))
        layout.addWidget(self.end_y_edit)
        layout.addWidget(self.end_y_edit)
        layout.addWidget(self.shape_label)
        layout.addLayout(shape_layout)
        layout.addWidget(self.length_label)
        layout.addWidget(self.length_edit)
        layout.addWidget(self.width_label)
        layout.addWidget(self.width_edit)
        layout.addWidget(self.radius_label)
        layout.addWidget(self.radius_edit)
        layout.addWidget(self.calculate_button)

        # Set the central widget of the window
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def toggle_input_fields(self):
        """
        Toggles the visibility of the input fields based on the selected shape.
        """
        if self.circle_radio.isChecked():
            self.length_label.hide()
            self.length_edit.hide()
            self.width_label.hide()
            self.width_edit.hide()
            self.radius_label.show()
            self.radius_edit.show()
        else:
            self.length_label.show()
            self.length_edit.show()
            self.width_label.show()
            self.width_edit.show()
            self.radius_label.hide()
            self.radius_edit.hide()


    def calculate(self):
        try:
            # Read coordinates from input fields
            start_x = float(self.start_x_edit.text())
            start_y = float(self.start_y_edit.text())
            end_x = float(self.end_x_edit.text())
            end_y = float(self.end_y_edit.text())
            end_y = float(self.end_y_edit.text())
            end_y = float(self.end_y_edit.text())
            
            #If Circle
            if self.circle_radio.isChecked(): 
                radius = float(self.radius_edit.text())
                
            #If Rectangle  
            else:
                length = float(self.length_edit.text())
                width = float(self.width_edit.text())
            

            # Run the external script and capture the output
            #If Circle
            if self.circle_radio.isChecked(): 
                result = subprocess.run(
                    ['python', 'a_star.py', str(start_x), str(start_y), str(end_x), str(end_y), str(radius)],
                    capture_output=True, text=True
                )
            #If Rectangle
            else: 
                result = subprocess.run(
                    ['python', 'a_star.py', str(start_x), str(start_y), str(end_x), str(end_y), str(length), str(width)],
                    capture_output=True, text=True
                )


            # Check for errors
            if result.returncode != 0:
                QMessageBox.warning(self, "Error", f"Script error: {result.stderr.strip()}")
                return

            #Display the result
            #distance = result.stdout.strip()
            #QMessageBox.information(self, "Result", f"Calculated distance: {distance}")

        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numbers.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RobotGUI()
    window.show()
    sys.exit(app.exec_())
