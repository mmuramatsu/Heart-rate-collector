import asyncio
import datetime
import time as ts

from bleak import BleakClient
import matplotlib.pyplot as plt
from PyQt5.QtCore import QThread, pyqtSignal

from lib.Data_ecg import Data_ecg
from lib.Data_rr import Data_rr


# UUID for model number
MODEL_NBR_UUID = '00002a24-0000-1000-8000-00805f9b34fb'
# UUID for manufacturer name
MANUFACTURER_NAME_UUID = '00002a29-0000-1000-8000-00805f9b34fb'
# UUID for battery level
BATTERY_LEVEL_UUID = '00002a19-0000-1000-8000-00805f9b34fb'
# UUID for Heart Rate Measurement
HEART_RATE = '00002a37-0000-1000-8000-00805f9b34fb'
# UUID for connection establishment with device
PMD_SERVICE = 'FB005C80-02E7-1CAD-8ACD2D8DF0C8'
# UUID for request stream settings
PMD_CONTROL = 'FB005C81-02E7-F387-1CAD-8ACD2D8DF0C8'
# UUID for request start stream
PMD_DATA = 'FB005C82-02E7-F387-1CAD-8ACD2D8DF0C8'
# UUID for request ECG stream
ECG_WRITE = bytearray([0x02, 0x00, 0x00, 0x01, 0x82, 0x00, 0x01, 0x01, 0x0E, 0x00])


class Data_collector(QThread):
    '''
    Class responsible for performing data collection.
    '''

    # Variables that connect this thread with the main thread
    start_collecting = pyqtSignal()
    plot_signal = pyqtSignal(float, float)
    stop_signal = pyqtSignal()
    finished_signal = pyqtSignal()


    def __init__(self, address, display_graph, capture_ecg, save_current_time, experiment_name, participant_id):
        '''
        Initialize the class variables

        Parameters:
            address (str): MAC address of the device
            display_graph (boolean): flag that decides whether a graph with HR will be displayed or not
            capture_ecg (boolean): flag that decides whether ECG will be captured with the RR
            save_current_time (boolean): flag that decides if the current PC time will be saved.
        '''

        super().__init__()
        self.address = address
        self.display_graph = display_graph
        self.capture_ecg = capture_ecg
        self.save_current_time = save_current_time
        self.experiment_name = experiment_name
        self.participant_id = participant_id


    def run(self):
        '''
        Function that are started when this WorkerThread are startd

        This function perform the data collection
        '''

        self.interrupt_flag = False

        # This object stores the ECG recorded
        self.data_ecg = Data_ecg()

        # This object stores the ECG recorded
        self.data_rr = Data_rr()

        # Run the events
        loop = asyncio.new_event_loop()

        loop.run_until_complete(self.connect())

        if self.data_ecg.time != []:
            # Saving the Raw data (time, timestamp, ecg)
            self.data_ecg.save_raw_data(self.experiment_name + '-' + self.participant_id + '-ecg')

        if self.data_rr.time != []:
            # Saving the Raw data (time, hr, rr)
            self.data_rr.save_raw_data(self.experiment_name + '-' + self.participant_id + '-rr')

        # Send a signal to the main thread
        self.finished_signal.emit()


    def stop(self):
        '''
        This function stop the data collection
        '''

        # This method will be connected to the stop_signal
        self.interrupt_flag = True


    def parse_rr(self, sender, data):
        '''
        Parse the data receive from the device into numeric values and stores it in
        a Data object.

        Parameters:
            data (bytearray): Heart rate measurement received from the device
                Byte 0 - Flags:
                    Bit 0 - Heart rate value format: 0 -> UINT8 bpm, 1 -> UINT16 bpm
                    Bit 1..2 - Sensor contact status
                    Bit 3 - Energy expended status
                    Bit 4 - RR-interval: 0 -> No values are preent, 1 -> One or more
                    values are present
                    Bit 5, 6 and 7 - Unused
                Byte 1 - UINT8 BPM
                Byte 2..5 - UINT16 RR intervals
        '''

        # If the 4th bit of the bytearray is 1 then RR reads were sent
        if data[0] & 0b00010000 == 0b00010000:

            if self.save_current_time:
                t = datetime.datetime.now().time()
            else:
                if self.data_rr.time == []:
                    # Sets t0 to current time
                    self.data_rr.t0 = ts.time()
                    t = 0
                else:
                    t = ts.time() - self.data_rr.t0

            self.data_rr.time.append(t)

            # data[1] is the HR read
            hr = data[1]
            self.data_rr.hr_values.append(hr)

            # data[2:4] is the RR interval
            # Convert the bytes in UINT16
            rr = int.from_bytes(data[2:4], byteorder='little', signed=False)
            self.data_rr.rr_values.append(rr)

            if self.display_graph:
                # Plot the HR values list
                self.plot_signal.emit(t if not self.save_current_time else len(self.data_rr.time)-1, hr)

            print(f'Time: {t} s,   Heart rate: {hr} bpm,       RR-interval: {rr} ms')


    def parse_ecg(self, sender, data):
        '''
        Parse the data receive from the device into numeric values and stores it in
        a Data object.

        Parameters:
            data (bytearray): ECG measurement received from the device
        '''

        if data[0] == 0x00:
            if self.save_current_time:
                t = datetime.datetime.now().time()
            else:
                if self.data_ecg.time == []:
                    # Sets t0 to current time
                    self.data_ecg.t0 = ts.time()
                    t = 0.0
                else:
                    t = ts.time() - self.data_ecg.t0

            timestamp = self.convert_to_unsigned_long(data, 1, 8)
            step = 3
            samples = data[10:]
            offset = 0

            while offset < len(samples):
                ecg = self.convert_array_to_signed_int(samples, offset, step)
                offset += step
                self.data_ecg.time.extend([t])
                self.data_ecg.timestamp.extend([timestamp])
                self.data_ecg.ecg.extend([ecg])


    def convert_array_to_signed_int(self, data, offset, length):
        '''
        This function convert a bytearray in a signed int
        '''

        return int.from_bytes(
            bytearray(data[offset : offset + length]), byteorder='little', signed=True,
        )


    def convert_to_unsigned_long(self, data, offset, length):
        '''
        This function convert to a unsigned long
        '''

        return int.from_bytes(
            bytearray(data[offset : offset + length]), byteorder='little', signed=False,
        )


    async def check_connection(self, client):
        '''
        Check if the connection to the device has been established

        Parameters:
            client (BleakClient): Client connected to the device
        '''

        if client.is_connected:
            print("------ Device is connected ------")

            # Retrieve device characteristics

            model_number = await client.read_gatt_char(MODEL_NBR_UUID)
            print("Model Number: {0}".format("".join(map(chr, model_number))))

            manufacturer_name = await client.read_gatt_char(MANUFACTURER_NAME_UUID)
            print("Manufacturer Name: {0}".format("".join(map(chr, manufacturer_name))))

            battery_level = await client.read_gatt_char(BATTERY_LEVEL_UUID)
            print("Battery Level: {0}%".format(int(battery_level[0])))

        else:
            print('Error: Unable to connect to the device')


    async def process(self, client):
        '''
        This function will record the data receive from the device

        Parameters:
            client (BleakClient): Client connected to the device
        '''

        if client.is_connected:

            if self.capture_ecg:
                att_read = await client.read_gatt_char(PMD_CONTROL)

                await client.write_gatt_char(PMD_CONTROL, ECG_WRITE)

                # Start receiving ecg data
                await client.start_notify(PMD_DATA, self.parse_ecg)

            # Start receiving data
            await client.start_notify(HEART_RATE, self.parse_rr)

            self.start_collecting.emit()

            while not self.interrupt_flag:
                await asyncio.sleep(1)

            # Stop receiving data
            await client.stop_notify(HEART_RATE)

            if self.capture_ecg:
                await client.stop_notify(PMD_DATA)
        else:
            print('Error: Unable to connect to the device')


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

                print('------ Start to recording data ------')

                # Record the data
                task = asyncio.create_task(self.process(client))

                await asyncio.gather(task)
                print('------ Recording stopped  ------\n\n')

                await client.disconnect()

        except Exception as e:
            print(e)
