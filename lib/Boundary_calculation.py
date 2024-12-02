import numpy as np
from sklearn.metrics import mutual_info_score
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal
import warnings


def warn(*args, **kwargs):
    '''
    Function to don't display the warnings messages
    '''
    pass


warnings.warn = warn


class Boundary_calculation(QThread):
    '''
    Class responsible for performing boundary calculation.
    '''

    # Variables that connect this thread with the main thread
    finished_signal = pyqtSignal(float, list, list)


    def __init__(self, path):
        '''
        Initialize the class variables

        Parameters:
            path (string): path of the file with HRV values

        '''
        super().__init__()
        self.path = path


    def run(self):
        '''
        Function that are started when this WorkerThread are startd

        This function perform the boundary calculation using Mutual Info Score (MIS)
        '''

        # Open the .CSV and remove the NaN values
        df = pd.read_csv(self.path)
        df = df.dropna()

        # Getting the HRV and real_state from the dataset
        std = list(df['std'])
        real_state = list(df['real_state'])

        # Recreating the dataframe to shuffle all the data
        df = pd.DataFrame({'std':std, 'real_state':real_state[:len(std)]})

        # Temporary variables to make the plot in the end
        tmp1 = [i for i in range(len(list(df['std'])))]

        # Turn the data into lists to process the MIS
        std = list(df['std'])
        state = list(df['real_state'])

        # Combine and sort based on std values
        combined = sorted(zip(std, state), key=lambda x: x[0])

        # Calculate midpoints
        midpoints = [(combined[i][0] + combined[i+1][0]) / 2 for i in range(len(combined) - 1)]

        best_threshold = None
        best_score = 0

        for midpoint in midpoints:
            # Compute information gain for the split
            info_gain = mutual_info_score(std, [1 if value > midpoint else 0 for value in std])

            # Update best threshold if information gain is better
            if info_gain > best_score:
                best_score = info_gain
                best_threshold = midpoint

        print("Best division:", best_threshold)

        # Send a signal to the main thread
        self.finished_signal.emit(best_threshold, std, tmp1)