import pandas as pd

from lib.Data import Data


class Data_ecg(Data):
    '''
    Data objects will stores the data received from the device.
    '''

    def __init__(self):
        super().__init__()

        self.timestamp = []
        self.ecg = []


    def save_raw_data(self):
        '''
        Save the all triples (time, timestamp, ECG) received from the Polar H10.
        '''

        filename = 'raw_ecg-' + self.get_time() + '.csv'

        print (f'------ Save raw data in \"{filename}\" ------\n\n')

        df = pd.DataFrame(data={'time': self.time,
                                'timestamp': self.timestamp,
                                'ecg': self.ecg
        })

        df.to_csv(filename, sep=',', header=True)
