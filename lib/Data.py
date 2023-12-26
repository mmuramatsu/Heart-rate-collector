import datetime


TIME_UNINITIALIZED = -1

class Data:
    '''
    Data objects will stores the data received from the device.
    '''

    def __init__(self):
        self.t0 = TIME_UNINITIALIZED
        self.time = []


    def get_time(self):
        current_time = datetime.datetime.now()

        return str(current_time)
