import asyncio

from bleak import BleakScanner
from PyQt5.QtCore import QThread, pyqtSignal

class Scan(QThread):
    '''
    Class responsible for performing scan task.
    '''

    # Variables that connect this thread with the main thread
    log_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal()

    def __init__(self):
        '''
        Initialize the class variables
        '''

        super().__init__()


    def run(self):
        '''
        Function that are started when this WorkerThread are startd

        This function perform the scan task
        '''

        # Run the events
        loop = asyncio.new_event_loop()

        loop.run_until_complete(self.scan())

        self.finished_signal.emit()


    async def scan(self):
        '''
        This function scan for nearby bluetooth devices and print their
        characteristics.

        Note: You can use this function to identify the MAC Address of the device.
        '''

        print('------ Scanning for devices -------')

        devices = await BleakScanner.discover()
        for d in devices:
            name = d.name
            address = d.address
            print('Device name: ', name)
            print('MAC Address: ', address)
            #print('Metadata: ')
            #print(d.metadata)
            print('\n')

            if "Polar" in name:
                self.log_signal.emit(name, address)

        print('\n\n')
