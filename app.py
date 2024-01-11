import asyncio
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QCheckBox, QDesktopWidget, QDialog, QMessageBox, QStatusBar, QLineEdit, QSpacerItem, QSizePolicy

from lib.Check_status import Check_status
from lib.Collect_window import Collect_window
from lib.Scan import Scan


class MainWindow(QMainWindow):
    '''
    Class responsible for building and implementing the main interface functionalities.
    '''

    def __init__(self):
        '''
        Initialize the UI class
        '''

        super().__init__()

        self.init_ui()

    def init_ui(self):

        self.setGeometry(0, 0, 500, 270)

        # Setting a central widget to the MainWindow
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout()

        # Create horizontal layout for label, dropdown, and "Scan" button
        line_layout = QHBoxLayout()

        # Create label
        label = QLabel('Select device:', self)

        # Create dropdown
        self.devices_dropdown = QComboBox(self)

        # Create scan button
        self.scan_button = QPushButton('Scan', self)
        self.scan_button.clicked.connect(self.scan_devices)

        # Add widgets to the line layout
        line_layout.addWidget(label)
        line_layout.addWidget(self.devices_dropdown)
        line_layout.addWidget(self.scan_button)

        # Add the line layout to the main layout
        layout.addLayout(line_layout)

        # Create "Check device status" button
        self.check_status_button = QPushButton('Check device status', self)
        self.check_status_button.clicked.connect(self.check_status)

        # Create "Start collecting" button
        self.start_collecting_button = QPushButton('Start collecting', self)
        self.start_collecting_button.clicked.connect(self.start_collecting)

        # Add additional buttons to the main layout
        layout.addWidget(self.check_status_button)

        # Add vertical spacer
        spacer = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        # Create labels and line edits
        output_filename_label = QLabel('Output filename:')

        self.output_filename_edit = QLineEdit()

        line_layout = QHBoxLayout()
        line_layout.addWidget(output_filename_label)
        line_layout.addWidget(self.output_filename_edit)

        # Add the line layout to the main layout
        layout.addLayout(line_layout)

        # Create horizontal layout for checkboxes
        checkbox_layout = QHBoxLayout()

        # Create "Display graph" checkbox
        self.display_graph_checkbox = QCheckBox('Display graph', self)

        # Create "Collect ECG" checkbox
        self.collect_ecg_checkbox = QCheckBox('Collect ECG', self)

        # Create "Save current time" checkbox
        self.save_current_time_checkbox = QCheckBox('Save current time', self)

        # Add checkboxes to the horizontal layout
        checkbox_layout.addWidget(self.display_graph_checkbox)
        checkbox_layout.addWidget(self.collect_ecg_checkbox)
        checkbox_layout.addWidget(self.save_current_time_checkbox)

        # Add the checkbox layout to the main layout
        layout.addLayout(checkbox_layout)

        # Add vertical spacer
        spacer = QSpacerItem(20, 2, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        layout.addWidget(self.start_collecting_button)

        # Status bar
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # Link to a external site
        site_link = QLabel('Developed by: <a href="https://mmuramatsu.com">mmuramatsu</a>')
        site_link.setOpenExternalLinks(True)
        status_bar.addPermanentWidget(site_link)

        # Set layout for the main window
        central_widget.setLayout(layout)

        # Set window properties
        self.setWindowTitle('Heart rate collector')

        # Center the window on the screen
        self.center_window()

        self.show()


    def center_window(self):
        '''
        This function moves the window to the center
        '''

        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())


    def disable_all_buttons(self):
        '''
        Disable all buttons of the interface
        '''

        self.scan_button.setEnabled(False)
        self.check_status_button.setEnabled(False)
        self.start_collecting_button.setEnabled(False)


    def enable_all_buttons(self):
        '''
        Enable all buttons of the interface
        '''

        self.scan_button.setEnabled(True)
        self.check_status_button.setEnabled(True)
        self.start_collecting_button.setEnabled(True)


    def scan_devices(self):
        '''
        This functions starts a WorkerThread to run a bluetooth scan
        '''

        self.disable_all_buttons()
        self.devices_dict = {}

        # Create the worker thread to scan the bluetooth devices without locking the main thread
        self.worker_thread = Scan()
        self.worker_thread.log_signal.connect(self.update_devices_list)
        self.worker_thread.finished_signal.connect(self.scan_finished)

        # Start the worker thread
        self.worker_thread.start()


    def update_devices_list(self, name='test', address='test'):
        '''
        This function add a new device to the list of devices.

        This function are called when the Scan WorkerThread send a signal to the MainThread.

        Parameters:
            name (str): name of the founded device
            address (str): MAC address of the device founded
        '''

        self.devices_dict[name] = address


    def scan_finished(self):
        '''
        This function are called when the Scan WorkerThread are fineshed.

        Adds the finded devices to the dropdown list
        '''

        # Clear the dropdown before adding new values
        self.devices_dropdown.clear()

        # Populate the dropdown with sample values
        self.devices_dropdown.addItems(list(self.devices_dict.keys()))

        self.enable_all_buttons()


    def check_status(self):
        '''
        This functions starts a WorkerThread that get device status
        '''

        if self.devices_dropdown.currentText() == '':
            QMessageBox.warning(self, "Error", "No devices selected\nSelect a device first.")
            return

        self.disable_all_buttons()

        address = self.devices_dict[self.devices_dropdown.currentText()]

        # Create the worker thread with the number of steps
        self.worker_thread = Check_status(address)
        self.worker_thread.finished_signal.connect(self.check_status_finished)

        # Start the worker thread
        self.worker_thread.start()


    def check_status_finished(self, status, model, uuid, battery):
        '''
        This function are called when the Check_status WorkerThread are fineshed.

        Show the device status in a Dialog window
        '''

        dialog = QDialog(self)
        dialog.setWindowTitle("Device Status")
        #dialog.setGeometry(self.parent_x, self.parent_y, 400, 200)

        if not status:
            model_label = QLabel(model)
            uuid_label = QLabel(uuid)
            battery_label = QLabel(battery)

            layout = QVBoxLayout(dialog)

            layout.addWidget(model_label)
            layout.addWidget(uuid_label)
            layout.addWidget(battery_label)
        else:
            error_label = QLabel(model)
            layout = QVBoxLayout(dialog)

            layout.addWidget(error_label)

        dialog.exec_()  # Use exec_() to display the dialog

        self.enable_all_buttons()


    def start_collecting(self):
        '''
        This functions display the Collecting window and starts to collect data
        '''

        # If there is no selected devices
        if self.devices_dropdown.currentText() == '':
            QMessageBox.warning(self, "Error", "No devices selected\nSelect a device first.")
            return
        
        # If output filename field is empty
        if self.output_filename_edit.text() == '':
            QMessageBox.warning(self, "Error", "The field \"Output filename\" is empty.")
            return
        
        address = self.devices_dict[self.devices_dropdown.currentText()]

        self.hide()
        self.collect_window = Collect_window(self,
                                            self.devices_dropdown.currentText(),
                                            address,
                                            self.display_graph_checkbox.isChecked(),
                                            self.collect_ecg_checkbox.isChecked(),
                                            self.save_current_time_checkbox.isChecked(),
                                            self.output_filename_edit.text(),
        )
        self.collect_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
