import asyncio
import datetime
import time as ts

import pandas as pd
from pynput.keyboard import Key, Listener, KeyCode, Controller
from PyQt5.QtCore import QThread, pyqtSignal


class Tapping_thread(QThread):
    '''
    Class responsible for performing tapping experiment.
    '''

    # Variables that connect this thread with the main thread
    stop_signal = pyqtSignal()
    finished_signal = pyqtSignal()


    def __init__(self, save_current_time, output_filename):
        '''
        Initialize the class variables

        Parameters:
            save_current_time (boolean): flag that decides if the current PC time will be saved;
            output_filename (string): filename of the ouput file.
        '''

        super().__init__()
        self.save_current_time = save_current_time
        self.output_filename = output_filename


    def run(self):
        '''
        Function that are started when this WorkerThread are startd

        This function perform the tapping experiment
        '''

        self.t0 = None
        self.tapping_timestamp = []
        self.tapping_machine_timestamp = []

        # Setting the listener to always catch the keyboard input
        self.listener = Listener(on_press=self.on_press)

        # Listenning to all keyboard input
        with self.listener:
            self.listener.join()

        # Release the RIGHT key after listener was unlock
        key = Controller()
        key.release(Key.right)

        print('------ Tapping experiment was stopped. ------\n\n')

        self.save()

        self.finished_signal.emit()


    def on_press(self, key):
        '''
        Function called when a key was pushed

        key (KeyCode): represents the key pressed
        '''

        if key == KeyCode.from_char('b'):
            if self.tapping_timestamp == []:
                # Sets t0 to current time
                self.t0 = ts.time()
                t = 0
            else:
                t = ts.time() - self.t0

            self.tapping_timestamp.append(t)

            if self.save_current_time:
                cur_t = datetime.datetime.now().time()
                self.tapping_machine_timestamp.append(cur_t)

            print('\'B\' was pressed in: ', t)


    def save(self):
        '''
        Save the timestamps when the \'B\' key was pressed.
        '''

        current_time = datetime.datetime.now()

        filename = self.output_filename + '-tapping-' + str(current_time) + '.csv'

        print (f'------ Save tapping in \"{filename}\" ------\n\n')

        if not self.save_current_time:
            df = pd.DataFrame(data={'timestamp': self.tapping_timestamp,})
        else:
            df = pd.DataFrame(data={'timestamp': self.tapping_timestamp,
                                    'current_time': self.tapping_machine_timestamp,
            })

        df.to_csv(filename, sep=',', header=True)


    def stop(self):
        '''
        This function stop the tapping experiment

        This method will be connected to the stop_signal
        '''

        # Stop the listener
        self.listener.stop()

        # Force a pressing on RIGHT key just to unlock the listener
        key = Controller()
        key.press(Key.right)