from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, QSplitter, QTabWidget, QFormLayout, QScrollArea ,QHBoxLayout,QMessageBox , QGridLayout ,QSlider 
from PySide6.QtGui import QPixmap,QIcon
from PySide6.QtCore import Qt
from .ClickableWidget import ClickableWidget
import json
import requests

from qt_material import apply_stylesheet
from view.View import View
       
class QtView(View):
    def __init__(self):
        super().__init__()

        # Initialize Qt application
        self.app = QApplication([])

        # Create main window
        self.window = QMainWindow()

        # set the window title
        self.window.setWindowTitle("Plan Command Center")

        # set an icon for the window
        self.window.setWindowIcon(QIcon("view/Skull-Icon.svg.png"))
        
        # set window size
        self.window.resize(1000, 600)
        self.window.setMinimumSize(self.window.size())
        self.window.setMaximumSize(self.window.size())

        self.delete_button = QPushButton("Delete", self.window)
        # Add a flag to track whether the submit button has been clicked
        self.submit_clicked = False
        # Add a flag to track whether the address is valid
        self.address_validated = False
        # The data of the current request
        self.current_data = None
        
        self.id_for_oporations = -1

        # Initialize addresses as an empty JSON array
        self.history = json.loads('[]')  # Initialize as an empty JSON array

        # Create a central widget for the main window
        self.central_widget = QWidget()
        self.window.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Create a tab widget
        self.tab_widget = QTabWidget(self.central_widget)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        self.layout.addWidget(self.tab_widget)

        # Initialize tabs
        self.init_first_tab()
        self.init_second_tab()
        self.init_third_tab()

        # Apply a theme to the application
        apply_stylesheet(self.app, theme='dark_blue.xml')

    def init_first_tab(self):
        # First tab
        self.first_tab = QWidget()
        self.first_layout = QFormLayout(self.first_tab)
        
        self.address_label = QLabel("Enter Address:")
        self.address_line_edit = QLineEdit(self.first_tab)
        self.address_line_edit.setStyleSheet("color: white;")
        self.first_layout.addRow(self.address_label, self.address_line_edit)

        self.zoom_label = QLabel("Enter Zoom Level:")
        self.zoom_slider = QSlider(Qt.Horizontal, self.first_tab)
        self.zoom_slider.setStyleSheet("color: white;")
        self.zoom_slider.setMinimum(1)  # Set the minimum value
        self.zoom_slider.setMaximum(20)  # Set the maximum value
        self.zoom_value_label = QLabel()  # Create a label to display the slider's value
        self.zoom_slider.valueChanged.connect(lambda: self.zoom_value_label.setText(str(self.zoom_slider.value())))  # Update the label's text when the slider's value changes

        zoom_layout = QHBoxLayout()  # Create a horizontal layout
        zoom_layout.addWidget(self.zoom_slider)  # Add the slider to the layout
        zoom_layout.addWidget(self.zoom_value_label)  # Add the value label to the layout

        self.first_layout.addRow(self.zoom_label, zoom_layout)  # Add the label and the layout (containing the slider and the value label) to the row

        self.submit_button = QPushButton("Submit", self.first_tab)
        self.submit_button.setEnabled(True) 
        self.first_layout.addRow(self.submit_button)
        
        #the hidden message will be hidden and when shown the text will be error's red
        self.hidden_message = QLabel("")
        self.hidden_message.setStyleSheet("color: red;")
        self.hidden_message.setAlignment(Qt.AlignCenter)  # Center the text
        self.first_layout.addRow(self.hidden_message)
        
        self.tab_widget.addTab(self.first_tab, "Address and Date")

    def init_second_tab(self):
        # Second tab
        self.second_tab = QWidget()
        self.second_layout = QHBoxLayout(self.second_tab)  # Change to QHBoxLayout

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self.second_tab)  # Change to Horizontal
        self.second_layout.addWidget(self.splitter)

        # Left widget with image holder
        self.left_widget = QWidget(self.second_tab)
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setAlignment(Qt.AlignCenter)  # Align the layout to the center

        self.image_label = QLabel(self.left_widget)
        self.pixmap = QPixmap()

        self.image_label.setScaledContents(True)  # Add this line
        self.image_label.setAlignment(Qt.AlignCenter)  # Align the image label to the center
        self.left_layout.addWidget(self.image_label)

        self.splitter.addWidget(self.left_widget)

        # Right widget with text presenter, text input, and send button
        self.right_widget = QWidget(self.second_tab)
        self.right_layout = QVBoxLayout(self.right_widget)

        self.input_label = QLabel("Input:", self.right_widget)  # Rename the header for the input
        self.right_layout.addWidget(self.input_label)

        self.prompt_line = QLineEdit(self.right_widget)
        self.prompt_line.setStyleSheet("color: white;")
        self.right_layout.addWidget(self.prompt_line)

        self.send_button = QPushButton("Send", self.right_widget)
        self.right_layout.addWidget(self.send_button)

        # Create a scroll area for the display label
        self.scroll_area = QScrollArea(self.right_widget)
        self.scroll_area.setWidgetResizable(True)  # Allow the widget to resize

        # Create a scroll area for the display label
        self.scroll_area = QScrollArea(self.right_widget)
        self.scroll_area.setWidgetResizable(True)  # Allow the widget to resize
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # Always show vertical scroll bar
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Always hide horizontal scroll bar

        # Create a widget for the scroll area
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)

        self.display_label = QLabel(self.scroll_widget)  # Define the display_label here
        self.display_label.setWordWrap(True)  # Enable word wrapping
        self.scroll_layout.addWidget(self.display_label)

        # Set the scroll widget as the widget for the scroll area
        self.scroll_area.setWidget(self.scroll_widget)

        self.right_layout.addWidget(self.scroll_area)  # Add the scroll area to the layout right after the send button

        self.splitter.addWidget(self.right_widget)

        # Set the stretch factors of the widgets in the splitter
        self.splitter.setStretchFactor(0, 0)  # Set the stretch factor of the left widget to 0
        self.splitter.setStretchFactor(1, 1)  # Set the stretch factor of the right widget to 1

        # Make the splitter handle not movable
        self.splitter.setHandleWidth(0)


        self.tab_widget.addTab(self.second_tab, "Map and Response")

    def init_third_tab(self):
        # Third tab (history of requests)
        self.third_tab = QWidget()
        self.third_layout = QVBoxLayout(self.third_tab)

        self.history_label = QLabel("History of Requests:", self.third_tab)
        self.third_layout.addWidget(self.history_label)


        self.tab_widget.addTab(self.third_tab, "History")
        

    def display_data(self, data):
        self.current_data = data
        url = data.get("url")
        image_data = requests.get(url).content
        self.pixmap.loadFromData(image_data)
        self.image_label.setPixmap(self.pixmap)        # Set a fixed size for the image label
        self.image_label.setFixedSize(self.image_label.pixmap().width(), self.image_label.pixmap().height())
        self.hidden_message.setText("")  # Clear the hidden message
        self.address_validted = True
        self.submit_clicked = True  # Set the flag to True when the submit button is clicked
        self.tab_widget.setCurrentIndex(1)  # Move to the second tab

    def get_user_input(self):
        return self.prompt_line.text()

    def show_message(self, message):
        self.display_label.setText(message)

    def end_program(self, message):
        self.show_message(message)
        self.window.close()
    
    """
            Display a message box with the given message.
    """ 
    def show_message(self, message):
        msgBox = QMessageBox()
        msgBox.setText(message)
        msgBox.exec()
        
    def delete_clicked(self,id):
        
        self.id_for_oporations = id
        # click menullay the delete button
        self.delete_button.click()
        
    def resend_clicked(self,id):
        self.id_for_oporations = id
        # click menullay the resend button
        self.send_button.click()
        # move manually to the second tab
        self.tab_widget.setCurrentIndex(1)
        

    def tab_changed(self, index):
        if index == 2:  # If the current tab is the "History" tab
            return  # Do nothing and allow the user to access the tab
        elif not self.submit_clicked and index == 1:
            self.tab_widget.setCurrentIndex(0)  # Force stay on the first tab
        elif index == 0:
            self.submit_clicked = False  # Reset the flag when moving back to the first tab
            self.tab_widget.setCurrentIndex(0)  # Force stay on the first tab
                 
    def history_init(self):
        self.scroll_area = QScrollArea(self.third_tab)
        # give the Scroll Area a different color
        self.scroll_area.setStyleSheet("background-color: #262a2e;")
        self.scroll_widget = QWidget()
        self.history_list_widget = QGridLayout(self.scroll_widget)

        for i, item in enumerate(self.history):
            widget = ClickableWidget(item.get("url"), item.get("location").get("address"),item ,self)
            row = i // 7  # change the number to set number of rows
            column = i % 5  # change the number to set number of columns
            
            self.history_list_widget.addWidget(widget, row, column)
            self.history_list_widget.setColumnStretch(column, 1)  # 
            self.history_list_widget.setRowStretch(row, 1)  # 

        self.scroll_area.setWidget(self.scroll_widget)
        self.third_layout.addWidget(self.scroll_area)
        
    def add_history(self, item):
        widget = ClickableWidget(item.get("url"), item.get("location").get("address"),item ,self)
        row = len(self.history) // 7 
        column = len(self.history) % 5 
        
        self.history_list_widget.addWidget(widget, row, column)
        self.history_list_widget.setColumnStretch(column, 1)  
        self.history_list_widget.setRowStretch(row, 1) 
        self.history.append(item)
        
        self.scroll_area.setWidget(self.scroll_widget)
        self.third_layout.addWidget(self.scroll_area)
        self.scroll_widget.adjustSize()  # Adjust the size of the widget
    
    def remove_history(self, id):
        # Find the index of the item with the specified id
        index = next((i for i, item in enumerate(self.history) if item.get('id') == id), None)
        if index is None:
            return  # Item not found

        row = index // 7
        column = index % 5

        # Remove the item from the history
        self.history.pop(index)

        # Remove the item from the view
        widget = self.history_list_widget.itemAtPosition(row, column).widget()
        widget.deleteLater()
        self.history_list_widget.setColumnStretch(column, 1)  
        self.history_list_widget.setRowStretch(row, 1) 
        self.scroll_widget.adjustSize()
        
    def startView(self):
        self.history_init()
        self.window.show()
        self.app.exec_()