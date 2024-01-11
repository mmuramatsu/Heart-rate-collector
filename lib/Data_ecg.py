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
        self.current_time = []


    def save_raw_data(self, filename=None, save_current_time=False):
        '''
        Save the all triples (time, timestamp, ECG) received from the Polar H10.
        '''

        filename = filename + '-' + self.get_time() + '.csv'

        print (f'------ Save raw data in \"{filename}\" ------\n\n')

        if not save_current_time:
            df = pd.DataFrame(data={'time': self.time,
                                    'timestamp': self.timestamp,
                                    'ecg': self.ecg
            })
        else:
            df = pd.DataFrame(data={'time': self.time,
                                    'current_time': self.current_time,
                                    'timestamp': self.timestamp,
                                    'ecg': self.ecg
            })

        df.to_csv(filename, sep=',', header=True)
