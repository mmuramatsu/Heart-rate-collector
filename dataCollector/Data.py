import numpy as np
import pandas as pd


class Data:
    '''
    Data objects will stores the data received from the device.
    '''

    def __init__(self):
        self.hr_values = []
        self.rr_values = []
        self.t0 = -1
        self.time = []


    def save_raw_data(self, filename):
        '''
        Save the all triples (time, hr, rr) received from the Polar H10.

        Parameters:
            filename (string): name from the output file
        '''

        if filename is not None:
            filename += '_'
        else:
            filename = ''

        filename += 'raw_data.csv'

        print (f'------ Save raw data in \"{filename}\" ------\n\n')

        df = pd.DataFrame(data=[self.time, self.hr_values, self.rr_values])
        df = df.T
        df.columns = ['time', 'heart rate', 'rr interval']
        df.to_csv(filename, sep=',', header=True)
