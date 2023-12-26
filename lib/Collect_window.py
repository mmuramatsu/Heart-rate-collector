import datetime

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QMessageBox, QDesktopWidget, QHBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.animation as animation
import matplotlib.pyplot as plt

from lib.Data_collector import Data_collector


class Collect_window(QMainWindow):
    '''
    Class responsible for building and implementing the data collection interface functionalities.
    '''

    def __init__(self, app_window, name, address, display_graph, capture_ecg, save_current_time):
        '''
        Initialize the data collection UI

        Paramesters:
            app_window (MainWindow): reference to the main interface
            name (str): name of the device
            address (str): MAC address of the device
            display_graph (boolean): flag that decides whether a graph with HR will be displayed or not
            capture_ecg (boolean): flag that decides whether ECG will be captured with the RR
            save_current_time (boolean): flag that decides if the current PC time will be saved.
        '''

        super(Collect_window, self).__init__()

        self.app_window = app_window
        self.address = address
        self.display_graph = display_graph
        self.capture_ecg = capture_ecg
        self.save_current_time = save_current_time

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
            self.x_data, self.y_data = [], []
            self.line, = self.ax.plot(self.x_data, self.y_data)

            # Set xlabel and ylabel
            self.ax.set_xlabel('Time (s)' if not self.save_current_time else 'Index')
            self.ax.set_ylabel('Heart rate (BPM)')

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

        if not self.is_processing:
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

        # Update the plot
        self.line.set_data(self.x_data, self.y_data)

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
        plt.ylabel('Heart rate (BPM)')
        plt.plot(self.x_data, self.y_data)

        current_time = datetime.datetime.now()

        filename = 'graph-' + str(current_time) + '.svg'
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
        )

        self.worker_thread.finished_signal.connect(self.collection_finished)
        self.worker_thread.start_collecting.connect(self.start_collecting_signal)
        self.worker_thread.plot_signal.connect(self.att_plot)
        self.worker_thread.stop_signal.connect(self.worker_thread.stop)

        # Start the worker thread
        self.worker_thread.start()


    def att_plot(self, x, y):
        '''
        This function add new values to the axis array

        Pamesters:
            x (float): time value
            y (int): HR value
        '''

        # Update data
        self.x_data.append(x)
        self.y_data.append(y)


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