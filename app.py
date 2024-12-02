import json
import os
import sys

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QCheckBox, QDesktopWidget, QDialog, QMessageBox, QStatusBar, QLineEdit, QSpacerItem, QSizePolicy, QFileDialog
from PyQt5.QtGui import QIntValidator

from lib.Boundary_calculation import Boundary_calculation
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

        self.init_config()

        self.init_ui()


    def init_ui(self):

        self.setGeometry(0, 0, 600, 500)

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
        self.devices_dropdown.setToolTip('Polar devices.')

        # Create scan button
        self.scan_button = QPushButton('Scan', self)
        self.scan_button.clicked.connect(self.scan_devices)
        self.scan_button.setToolTip('Seaching for Polar sensor devices.')

        # Add widgets to the line layout
        line_layout.addWidget(label)
        line_layout.addWidget(self.devices_dropdown)
        line_layout.addWidget(self.scan_button)

        # Add the line layout to the main layout
        layout.addLayout(line_layout)

        # Create "Check device status" button
        self.check_status_button = QPushButton('Check device status', self)
        self.check_status_button.clicked.connect(self.check_status)
        self.check_status_button.setToolTip('Get the selected device status (model, batery, etc.).')

        # Create "Settings" button

        self.settings_button = QPushButton('Experiment settings', self)
        self.settings_button.clicked.connect(self.settings)
        self.settings_button.setToolTip('Show a configuration window to set the experiments parameters.')

        # Create "Start collecting" button
        self.start_collecting_button = QPushButton('Start collecting', self)
        self.start_collecting_button.clicked.connect(self.start_collecting)
        self.start_collecting_button.setToolTip('Starts the data collection.')

        # Add additional buttons to the main layout
        layout.addWidget(self.check_status_button)

        # Add vertical spacer
        spacer = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        # Create labels and line edits
        output_filename_label = QLabel('Output filename:')

        self.output_filename_edit = QLineEdit()
        self.output_filename_edit.setToolTip('Set the output file name')

        line_layout = QHBoxLayout()
        line_layout.addWidget(output_filename_label)
        line_layout.addWidget(self.output_filename_edit)

        # Add the line layout to the main layout
        layout.addLayout(line_layout)

        # Create horizontal layout for checkboxes
        checkbox_layout = QHBoxLayout()

        # Create "Display graph" checkbox
        self.display_graph_checkbox = QCheckBox('Display graph', self)
        self.display_graph_checkbox.setToolTip('Display a (time, HR) graph during the data collection.')

        # Create "Collect ECG" checkbox
        self.collect_ecg_checkbox = QCheckBox('Collect ECG', self)
        self.collect_ecg_checkbox.setToolTip('Also collect ECG during the data collection.')

        # Create "Save current time" checkbox
        self.save_current_time_checkbox = QCheckBox('Save current time', self)
        self.save_current_time_checkbox.setToolTip('Save current machine time (HH:MM:SS) during the data collection.')

        # Add checkboxes to the horizontal layout
        checkbox_layout.addWidget(self.display_graph_checkbox)
        checkbox_layout.addWidget(self.collect_ecg_checkbox)
        checkbox_layout.addWidget(self.save_current_time_checkbox)

        # Add the checkbox layout to the main layout
        layout.addLayout(checkbox_layout)

        # Add vertical spacer
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        layout.addWidget(QLabel('Experiments variations:'))

        # Create "Tapping experiment" checkbox
        self.tapping_experiment_checkbox = QCheckBox('Tapping experiment', self)
        self.tapping_experiment_checkbox.setToolTip('During data collection, when the \'B\' key is pressed, the moment it was pressed will be saved in another file.')
        layout.addWidget(self.tapping_experiment_checkbox)

        # Add vertical spacer
        spacer = QSpacerItem(20, 2, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        layout.addWidget(self.settings_button)
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


    def init_config(self):
        '''
        Initialize the configuration file
        '''
        if os.path.isfile('config.json'):
            # Opening JSON file
            with open('config.json', 'r') as openfile:
                # Reading from json file
                self.setting_values = json.load(openfile)
        else:
            self.setting_values = {
                'representation_type': 0,
                'representation_type_value': 'Heart rate (BPM)',
                'window_limit': 0,
                'window_limit_value': 'All data',
                'rr_window' : '5',
                'display_states': False,
                'time_in_state_0': '40',
                'time_in_state_1': '40',
                'display_decision_boundary': False,
                'decision_boundary' : '100',
            }

            self.write_config_file(self.setting_values)


    def write_config_file(self, dictionary):
        '''
        Write the config on a JSON file
        '''
        with open('config.json', 'w') as outfile:
            json.dump(dictionary, outfile)


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
                                            self.tapping_experiment_checkbox.isChecked(),
                                            self.setting_values,
        )
        self.collect_window.show()


    def select_folder(self):
        '''
        '''
        # Open a folder selection dialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a File", "", "All Files (*);;Text Files (*.txt)")

        if file_path:  # If a folder is selected
            self.ok_button.setEnabled(False)
            self.find_best_boundary(file_path)


    def find_best_boundary(self, path):
        '''
        This function calculate the best boundary from a file.

        It is necessary to set a RR window size to calculate the sdNN correct
        '''
        # Create the worker thread with the number of steps
        self.worker_thread = Boundary_calculation(path)
        self.worker_thread.finished_signal.connect(self.find_best_boundary_finished)

        # Start the worker thread
        self.worker_thread.start()


    def find_best_boundary_finished(self, best_boundary, std, tmp1):
        '''
        Function are called when the WorkThread finished.

        This function shows a plot with the data and the best boundary.
        '''

        self.threshold_line_textbox.setText(str(best_boundary))

        dialog = QDialog(self)
        dialog.setWindowTitle("Best boundary")

        layout = QVBoxLayout(dialog)

        fig, ax = Figure(figsize=(10,8), dpi=100), None
        canvas = FigureCanvas(fig)
        canvas_widget = canvas
        layout.addWidget(canvas_widget)

        # Initial plot
        ax = fig.add_subplot(111)
        scatter = ax.scatter(tmp1, std)
        line, = ax.plot(tmp1, [best_boundary for _ in range(len(tmp1))], color='red')
        
        # Set xlabel and ylabel
        ax.set_xlabel('Window')
        ax.set_ylabel('sdNN')

        dialog.exec_()  # Use exec_() to display the dialog
        self.ok_button.setEnabled(True)

    
    def settings(self):
        '''
        Draw a window to manage collection settings
        '''

        default_values = self.setting_values

        dialog = QDialog(self)
        dialog.setWindowTitle("Experiment settings")
        #dialog.setGeometry(self.parent_x, self.parent_y, 400, 200)

        layout = QVBoxLayout(dialog)

        graph_settings = QLabel("Plot settings")
        layout.addWidget(graph_settings)

        h_layout = QHBoxLayout()

        representation_type = QLabel("Variable displayed:")
        representation_type_dropdown = QComboBox(self)
        representation_type_dropdown.addItems(['Heart rate (BPM)', 'sdNN'])
        representation_type_dropdown.setCurrentIndex(default_values['representation_type'])
        representation_type_dropdown.setToolTip('Variable to be displayed on the plot.')

        window_limit = QLabel("Amount of data presented:")
        window_limit_dropdown = QComboBox(self)
        window_limit_dropdown.addItems(['All data', '1 minute', '2 minutes', '3 minutes', '4 minutes', '5 minutes', '10 minutes'])
        window_limit_dropdown.setCurrentIndex(default_values['window_limit'])
        window_limit_dropdown.setToolTip('This setting adjusts the amount of data that will be displayed on the plot. For example, if \"1 minute\" is selected, then only the last 1 minute of data will be displayed.')

        h_layout.addWidget(representation_type)
        h_layout.addWidget(representation_type_dropdown)
        inner_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Maximum)
        h_layout.addItem(inner_spacer)
        h_layout.addWidget(window_limit)
        h_layout.addWidget(window_limit_dropdown)

        layout.addLayout(h_layout)

        h_layout = QHBoxLayout()

        rr_window_size = QLabel("RR window size:")
        rr_window_size_textbox = QLineEdit(default_values['rr_window'])
        rr_window_size_textbox.setValidator(QIntValidator(1,999))
        rr_window_size_textbox.setToolTip('Set the window size to calculate sdNN. Only used when \"sdNN\" is the representation type.')

        h_layout.addWidget(rr_window_size)
        h_layout.addWidget(rr_window_size_textbox)
        inner_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Maximum)
        h_layout.addItem(inner_spacer)

        layout.addLayout(h_layout)
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        h_layout = QHBoxLayout()

        # Create "Display states" checkbox
        display_state_checkbox = QCheckBox('Display states', self)
        display_state_checkbox.setChecked(default_values['display_states'])
        display_state_checkbox.setToolTip('Display different colors for the states.')

        h_layout.addWidget(display_state_checkbox)
        inner_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Maximum)
        h_layout.addItem(inner_spacer)

        layout.addLayout(h_layout)

        h_layout = QHBoxLayout()

        time_in_state_0 = QLabel("Time in state 0(s):")
        time_in_state_0_textbox = QLineEdit(default_values['time_in_state_0'])
        time_in_state_0_textbox.setValidator(QIntValidator(1,999))

        h_layout.addWidget(time_in_state_0)
        h_layout.addWidget(time_in_state_0_textbox)
        inner_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Maximum)
        h_layout.addItem(inner_spacer)

        layout.addLayout(h_layout)

        h_layout = QHBoxLayout()

        time_in_state_1 = QLabel("Time in state 1(s):")
        time_in_state_1_textbox = QLineEdit(default_values['time_in_state_1'])
        time_in_state_1_textbox.setValidator(QIntValidator(1,999))

        h_layout.addWidget(time_in_state_1)
        h_layout.addWidget(time_in_state_1_textbox)
        inner_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Maximum)
        h_layout.addItem(inner_spacer)

        layout.addLayout(h_layout)
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        h_layout = QHBoxLayout()

        # Create "Display threshold line" checkbox
        display_thershold_checkbox = QCheckBox('Display decision boundary line', self)
        display_thershold_checkbox.setChecked(default_values['display_decision_boundary'])
        display_thershold_checkbox.setToolTip('Display the setted threshold line in the plot.')

        h_layout.addWidget(display_thershold_checkbox)
        inner_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Maximum)
        h_layout.addItem(inner_spacer)

        layout.addLayout(h_layout)

        h_layout = QHBoxLayout()

        threshold_line = QLabel("Decision boundary value:")
        self.threshold_line_textbox = QLineEdit(default_values['decision_boundary'])
        self.threshold_line_textbox.setValidator(QIntValidator(1,999))

        # Create a button
        button = QPushButton("Calculate best boundary")
        button.clicked.connect(self.select_folder)

        h_layout.addWidget(threshold_line)
        h_layout.addWidget(self.threshold_line_textbox)
        h_layout.addWidget(button)

        layout.addLayout(h_layout)        

        def save_config():
            '''
            Function called when the save button are pressed.

            This function save the new settings.
            '''
            aux = []
            
            # Checking if there is any empty string
            aux.append(representation_type_dropdown.currentIndex())
            aux.append(representation_type_dropdown.currentText())
            aux.append(window_limit_dropdown.currentIndex())
            aux.append(window_limit_dropdown.currentText())
            aux.append(rr_window_size_textbox.text() if rr_window_size_textbox.text() != '' else self.setting_values['hrv_window'])
            aux.append(display_state_checkbox.isChecked())
            aux.append(time_in_state_0_textbox.text() if time_in_state_0_textbox.text() != '' else self.setting_values['time_in_state_0'])
            aux.append(time_in_state_1_textbox.text() if time_in_state_1_textbox.text() != '' else self.setting_values['time_in_state_1'])
            aux.append(display_thershold_checkbox.isChecked())
            aux.append(self.threshold_line_textbox.text() if self.threshold_line_textbox.text() != '' else self.setting_values['threshold_line'])


            self.setting_values = {
                'representation_type': aux[0],
                'representation_type_value': aux[1],
                'window_limit': aux[2],
                'window_limit_value': aux[3],
                'rr_window' : aux[4],
                'display_states': aux[5],
                'time_in_state_0': aux[6],
                'time_in_state_1': aux[7],
                'display_decision_boundary': aux[8],
                'decision_boundary' : aux[9],
            }

            self.write_config_file(self.setting_values)

            dialog.accept()

        # Create "Start collecting" button
        self.ok_button = QPushButton('Save', self)
        self.ok_button.clicked.connect(save_config)

        h_layout = QHBoxLayout()
        inner_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Maximum)
        h_layout.addItem(inner_spacer)
        h_layout.addWidget(self.ok_button)
        inner_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Maximum)
        h_layout.addItem(inner_spacer)

        layout.addLayout(h_layout)

        dialog.exec_()  # Use exec_() to display the dialog


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
