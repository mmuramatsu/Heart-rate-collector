import asyncio

from bleak import BleakClient
from PyQt5.QtCore import QThread, pyqtSignal

# UUID for model number
MODEL_NBR_UUID = '00002a24-0000-1000-8000-00805f9b34fb'
# UUID for manufacturer name
MANUFACTURER_NAME_UUID = '00002a29-0000-1000-8000-00805f9b34fb'
# UUID for battery level
BATTERY_LEVEL_UUID = '00002a19-0000-1000-8000-00805f9b34fb'


class Check_status(QThread):
    '''
    Class responsible for performing check status task.
    '''

    # Variable that connect this thread with the main thread
    finished_signal = pyqtSignal(int, str, str, str)

    def __init__(self, address):
        '''
        Initialize the class variables

        Parameters:
            address (str): MAC address of the device
        '''

        super().__init__()
        self.address = address


    def run(self):
        '''
        Function that are started when this WorkerThread are startd

        This function perform the check status task
        '''

        self.statusString = []

        # Run the events
        loop = asyncio.new_event_loop()

        status = loop.run_until_complete(self.connect())

        if not status:
            self.finished_signal.emit(status, self.statusString[0], self.statusString[1], self.statusString[2])
        else:
            self.finished_signal.emit(status, self.statusString[0], '', '')


    async def check_connection(self, client):
        '''
        Check if the connection to the device has been established

        Parameters:
            client (BleakClient): Client connected to the device
        '''

        if client.is_connected:
            # Retrieve device characteristics

            model_number = await client.read_gatt_char(MODEL_NBR_UUID)
            self.statusString.append("Model Number: {0}".format("".join(map(chr, model_number))))

            manufacturer_name = await client.read_gatt_char(MANUFACTURER_NAME_UUID)
            self.statusString.append("Manufacturer Name: {0}".format("".join(map(chr, manufacturer_name))))

            battery_level = await client.read_gatt_char(BATTERY_LEVEL_UUID)
            self.statusString.append("Battery Level: {0}%".format(int(battery_level[0])))

        else:
            self.statusString.append('Error: Unable to connect to the device')


    async def connect(self):
        '''
        Connected to the device
        '''

        print('------ Connecting to the Polar H10 ------\n\n')

        try:
            async with BleakClient(self.address) as client:

                # Check the connected
                task = asyncio.create_task(self.check_connection(client))

                await asyncio.gather(task)

                await client.disconnect()

        except Exception as e:
            print(e)
            self.statusString= [str(e)]
            return 1

        return 0
