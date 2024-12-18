import datetime

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QMessageBox, QDesktopWidget, QHBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.animation as animation
import matplotlib.pyplot as plt

from lib.Data_collector import Data_collector
from lib.Tapping_thread import Tapping_thread


WINDOW_LIMIT = {'All data': None, '1 minute': 60, '2 minutes': 120, '3 minutes': 180, '4 minutes': 240, '5 minutes': 300, '10 minutes': 600}

class Collect_window(QMainWindow):
    '''
    Class responsible for building and implementing the data collection interface functionalities.
    '''

    def __init__(self, app_window, name, address, display_graph, capture_ecg, save_current_time, output_filename, tapping_flag, setting_values):
        '''
        Initialize the data collection UI

        Paramesters:
            app_window (MainWindow): reference to the main interface;
            name (str): name of the device;
            address (str): MAC address of the device;
            display_graph (boolean): flag that decides whether a graph with HR will be displayed or not;
            capture_ecg (boolean): flag that decides whether ECG will be captured with the RR;
            save_current_time (boolean): flag that decides if the current PC time will be saved;
            output_filename (string): filename of the output files;
            tapping_flag (boolean): flag thta decides if the tapping experiment will occur.
            setting_values (dict): aditional settings for the experiment
        '''

        super(Collect_window, self).__init__()

        self.app_window = app_window
        self.address = address
        self.display_graph = display_graph
        self.capture_ecg = capture_ecg
        self.save_current_time = save_current_time
        self.output_filename = output_filename
        self.tapping_flag = tapping_flag
        self.setting_values = setting_values

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.central_layout = QVBoxLayout(self.central_widget)

        connecting2_label = QLabel('Connection to: ' + name, self)
        collecting_label = QLabel('Collecting: HR' + (', RR and ECG' if self.capture_ecg else ' and RR'), self)

        self.central_layout.addWidget(connecting2_label)
        self.central_layout.addWidget(collecting_label)

        if self.display_graph:
            self.figure, self.ax = Figure(figsize=(14,8), dpi=100), None
            self.canvas = FigureCanvas(self.figure)
            self.canvas_widget = self.canvas
            self.central_layout.addWidget(self.canvas_widget)

            # Initial plot
            self.ax = self.figure.add_subplot(111)
            self.x_data, self.y_data, self.state = [], [], []
            self.line, = self.ax.plot(self.x_data, self.y_data)
            if self.setting_values['display_decision_boundary']:
                self.threshold_line, = self.ax.plot(self.x_data, [setting_values['decision_boundary']]*len(self.x_data))

            if self.setting_values['display_states']:
                self.state_sign = self.ax.scatter([], [], color='red', marker='X', s=100)
                self.len_state_sign = 0
                self.state_points = []

            # Set xlabel and ylabel
            self.ax.set_xlabel('Time (s)' if not self.save_current_time else 'Index')
            self.ax.set_ylabel(self.setting_values['representation_type_value'])

            # Animation
            self.ani = animation.FuncAnimation(self.figure, self.update_plot, interval=1000, save_count=10)

            # Save graph button
            self.save_button = QPushButton('Save graph', self)
            self.save_button.clicked.connect(self.save_graph)
            self.save_button.setEnabled(False)

            h_save_button_layout = QHBoxLayout()
            h_save_button_layout.addWidget(self.save_button)
            h_save_button_layout.addStretch(1)
            self.central_layout.addLayout(h_save_button_layout)

        # Stop button
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop_animation)
        self.stop_button.setFixedSize(200, 70)
        self.stop_button.setEnabled(False)

        h_stop_button_layout = QHBoxLayout()
        h_stop_button_layout.addStretch(1)
        h_stop_button_layout.addWidget(self.stop_button)
        h_stop_button_layout.addStretch(1)
        self.central_layout.addLayout(h_stop_button_layout)

        self.is_animation_running = True

        self.is_processing = True
        self.tapping_is_processing = True

        # Center the window on the screen
        self.center_window()

        # Set window properties
        self.setWindowTitle('Collector')

        self.start()


    def closeEvent(self, event):
        '''
        This function change the closeEvent of this UI. The new event will return to the main UI

        If the graph is being presented, the user will need to confirm to exit the screen
        '''

        if not self.is_processing and ((self.tapping_flag and not self.tapping_is_processing) ^ (not self.tapping_flag)):
                if self.display_graph:
                    close = QMessageBox.question(self, "Quit?", "Are you sure want return?", QMessageBox.Yes | QMessageBox.No)

                    if close == QMessageBox.No:
                        event.ignore()
                        return
        else:
            QMessageBox.warning(self, "Error", "You need to stop the processing first.")
            event.ignore()
            return

        self.close()
        self.app_window.show()


    def center_window(self):
        '''
        This function moves the window to the center
        '''

        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())


    def stop_animation(self):
        '''
        This function stops the graph animation and send a signal to the WorkerThread to stop the data collecting
        '''

        # Emit the signal to stop the worker thread
        self.worker_thread.stop_signal.emit()

        # Emit the signal to stop the tapping experiment
        if self.tapping_flag:
            self.tapping_experiment_thread.stop_signal.emit()

        if self.display_graph:
            self.ani.event_source.stop()
            self.is_animation_running = False

        self.stop_button.setEnabled(False)


    def update_plot(self, _):
        '''
        This function update the plot, adding new values
        '''

        if not self.is_animation_running:
            return

        # Define a Window limit if is necessary
        limit = WINDOW_LIMIT[self.setting_values['window_limit_value']]

        # If a limit is not needed, all data will be used, otherwise data will be trimmed
        if limit == None or self.x_data == []:
            x, y, state = self.x_data, self.y_data, self.state
        else:
            x, y, state = self.x_data[-limit:], self.y_data[-limit:], self.state[-limit:]

        # Update the plot
        self.line.set_data(x, y)

        # Add a boundary line
        if self.setting_values['display_decision_boundary']:
            self.threshold_line.set_data(x, [int(self.setting_values['decision_boundary'])]*len(x))

        # Add the state change sign
        if self.setting_values['display_states']:
            if len(state) != self.len_state_sign and len(state) > 1:

                if state[-2] != state[-1]: 
                    self.state_points.append((x[-1], y[-1]))

                if len(self.state_points) > 0:
                    if self.state_points[0][0] < x[0]:
                        self.state_points = self.state_points[1:]

                    x_state, y_state = zip(*self.state_points)
                    self.state_sign.set_offsets(list(zip(x_state, y_state)))

        # Adjust plot limits if needed
        self.ax.relim()
        self.ax.autoscale_view()


    def save_graph(self):
        '''
        This function are called when the "Save graph" button are pressed.

        Just saves the graph generated by the data
        '''

        plt.figure(figsize=(14,8), dpi=100)
        plt.xlabel('Time (s)' if not self.save_current_time else 'Index')
        plt.ylabel(self.setting_values['representation_type_value'])
        plt.plot(self.x_data, self.y_data)

        if self.setting_values['display_decision_boundary']:
            plt.plot(self.x_data, [int(self.setting_values['decision_boundary'])]*len(self.x_data))

        if self.setting_values['display_states']:
            x_state, y_state = [], []
            for i in range(1, len(self.state)):
                if self.state[i-1] != self.state[i]:
                    x_state.append(self.x_data[i])
                    y_state.append(self.y_data[i])

            plt.scatter(x_state, y_state, color='red', marker='X', s=100)

        current_time = datetime.datetime.now()

        filename = self.output_filename + '-graph-' + str(current_time) + '.svg'
        plt.savefig(filename)

        QMessageBox.about(self, "Image saved", f"Image save as \"{filename}\".")


    def start(self):
        '''
        This functions starts a WorkerThread to run the data collection
        '''

        # Create the worker thread with the number of steps
        self.worker_thread = Data_collector(self.address,
                                            self.display_graph,
                                            self.capture_ecg,
                                            self.save_current_time,
                                            self.output_filename,
                                            self.setting_values,
        )

        self.worker_thread.finished_signal.connect(self.collection_finished)
        self.worker_thread.start_collecting.connect(self.start_collecting_signal)
        self.worker_thread.plot_signal.connect(self.att_plot)
        self.worker_thread.stop_signal.connect(self.worker_thread.stop)

        if self.tapping_flag:
            self.tapping_experiment_thread = Tapping_thread(self.save_current_time,
                                                            self.output_filename,
            )

            self.tapping_experiment_thread.stop_signal.connect(self.tapping_experiment_thread.stop)
            self.tapping_experiment_thread.finished_signal.connect(self.tapping_thread_finished)

        # Start the worker thread
        self.worker_thread.start()


    def att_plot(self, x, y, state):
        '''
        This function add new values to the axis array

        Pamesters:
            x (float): time value
            y (int): HR value
        '''

        # Update data
        self.x_data.append(x)
        self.y_data.append(y)
        self.state.append(state)


    def collection_finished(self):
        '''
        This function are called when the WorkerThread are finished
        '''

        self.is_processing = False

        if self.display_graph:
            self.save_button.setEnabled(True)

        QMessageBox.about(self, "Process complete", "The processing is complete. All data are saved in .csv files.")
        return


    def start_collecting_signal(self):
        '''
        This function are called when the data collecting start, enabling the "Stop" button
        '''

        self.stop_button.setEnabled(True)

        # Start tapping thread
        if self.tapping_flag:
            self.tapping_experiment_thread.start()

    
    def tapping_thread_finished(self):
        '''
        This function are called when the Tapping thread are finished
        '''

        self.tapping_is_processing = False
        return