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


    def save_raw_data(self, filename=None, save_current_time=False):
        '''
        Save the all triples (time, hr, rr) received from the Polar H10.
        '''

        filename = filename + '-' + self.get_time() + '.csv'

        print (f'------ Save raw data in \"{filename}\" ------\n\n')

        if not save_current_time:
            df = pd.DataFrame(data={'time': self.time,
                                    'heart_rate': self.hr_values,
                                    'rr_interval': self.rr_values
            })
        else:
            df = pd.DataFrame(data={'time': self.time,
                                    'current_time': self.current_time,
                                    'heart_rate': self.hr_values,
                                    'rr_interval': self.rr_values
            })

        df.to_csv(filename, sep=',', header=True)
