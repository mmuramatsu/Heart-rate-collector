import pandas as pd

from lib.Data import Data


class Data_rr(Data):
    '''
    Data objects will stores the data received from the device.
    '''

    def __init__(self):
        super().__init__()

        self.hr_values = []
        self.rr_values = []
        self.current_time = []
        self.std = []

        self.state = [0]
        self.current_state = 0
        self.count_state = 0


    def save_raw_data(self, filename=None, save_current_time=False, additional_var=None):
        '''
        Save the all triples (time, hr, rr) received from the Polar H10.
        '''

        filename = filename + '-' + self.get_time() + '.csv'

        print (f'------ Save raw data in \"{filename}\" ------\n\n')

        data_columns = [self.time, self.hr_values, self.rr_values]
        data_columns_names = ['time', 'heart rate', 'rr interval']

        if save_current_time:
            data_columns = [self.time, self.current_time, self.hr_values, self.rr_values]
            data_columns_names = ['time', 'current_time', 'heart rate', 'rr interval']

        if additional_var == 'sdNN':
            data_columns.append(self.std)
            data_columns_names.append('sdNN')

        df = pd.DataFrame(data=data_columns)
        df = df.T
        df.columns = data_columns_names

        df.to_csv(filename, sep=',', header=True)