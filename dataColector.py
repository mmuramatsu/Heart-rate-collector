import argparse
import asyncio
import os
import signal
import sys
import time as ts

from bleak import BleakClient
from bleak import BleakScanner
import matplotlib.pyplot as plt

from Data import Data


def parse_data(sender, data):
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

        if rec_data.time == []:
            # Sets t0 to current time
            rec_data.t0 = ts.time()
            t = 0
        else:
            t = ts.time() - rec_data.t0

        rec_data.time.append(t)

        # data[1] is the HR read
        hr = data[1]
        rec_data.hr_values.append(hr)

        # data[2:4] is the RR interval
        # Convert the bytes in UINT16
        rr = int.from_bytes(data[2:4], byteorder='little', signed=False)
        rec_data.rr_values.append(rr)

        print(f'Time: {t} s,   Heart rate: {hr} bpm,       RR-interval: {rr} ms')


def signal_handler(sig, frame):
    '''
    Handles the interrupt signal
    '''

    print('\b\bKeyboard interrupt received...')
    global interrupt_flag
    interrupt_flag = True


async def check_connection(client):
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


async def process(client):
    '''
    This function will record the data receive from the device

    Parameters:
        client (BleakClient): Client connected to the device
    '''

    if client.is_connected:
        # Start receiving data
        await client.start_notify(HEART_RATE, parse_data)

        # Setup the plot
        plt.ion()
        fig = plt.figure()
        plt.title('Values of HR for each second')
        plt.ylabel('Heart Rate (BPM)')
        plt.xlabel('Time (s)')

        # Start to listening the SIGINT signal
        signal.signal(signal.SIGINT, signal_handler)

        while not interrupt_flag:
            await asyncio.sleep(1)

            # Plot the HR values list
            plt.plot(rec_data.time, rec_data.hr_values, color='red')
            plt.pause(0.01)

        plt.show()

        # Stop receiving data
        await client.stop_notify(HEART_RATE)

    else:
        print('Error: Unable to connect to the device')


async def connect(test_flag):
    '''
    Connected to the device
    '''

    print('------ Connecting to the Polar H10 ------\n\n')

    try:
        async with BleakClient(ADDRESS) as client:

            # Check the connected
            task = asyncio.create_task(check_connection(client))

            await asyncio.gather(task)

            print('\n\nPress ENTER to start recording data')
            input()

            print('------ Start to recording data ------')
            print('Press CRTL+C to stop the recording\n\n')

            # Record the data
            task = asyncio.create_task(process(client))

            await asyncio.gather(task)
            print('------ Recording stopped  ------\n\n')

            await client.disconnect()

    except Exception as e:
        print(e)


async def scan():
    '''
    This function scan for nearby bluetooth devices and print their
    characteristics.

    Note: You can use this function to identify the MAC Address of the device.
    '''

    print('------ Scanning for devices -------')

    devices = await BleakScanner.discover()
    for d in devices:
        print('Device name: ', d.name)
        print('MAC Address: ', d.address)
        print('Metadata: ')
        print(d.metadata)
        print('\n')

    print('\n\n')


if __name__ == '__main__':

    # Setup the arguments passed from the command line
    parser = argparse.ArgumentParser()

    ## The '-n' flag will be used to pass a name to the output files
    parser.add_argument('-n', '--namefile',
            help='define a name for the output file')

    ## The '-t' flag indicates that the program should be run in test mode
    parser.add_argument('-t', '--test', help='run the program in test mode',
            action='store_true')

    # Parse all arguments received from command line
    args = parser.parse_args()

    #  Setup the variable
    test_flag = False

    if args.test:
        test_flag = True
        print('\n\nRunning in test mode. No data will be saved\n\n')

    namefile = None

    if args.namefile:
        namefile = args.namefile

    # MAC address of the device
    ADDRESS = 'E2:26:96:80:8D:94'

    # UUID for model number
    MODEL_NBR_UUID = '00002a24-0000-1000-8000-00805f9b34fb'

    # UUID for manufacturer name
    MANUFACTURER_NAME_UUID = '00002a29-0000-1000-8000-00805f9b34fb'

    # UUID for battery level
    BATTERY_LEVEL_UUID = '00002a19-0000-1000-8000-00805f9b34fb'

    # UUID for Heart Rate Measurement
    HEART_RATE = '00002a37-0000-1000-8000-00805f9b34fb'

    # Interrupt flag
    interrupt_flag = False

    # This object stores the data recorded
    rec_data = Data()

    # Run the events
    loop = asyncio.get_event_loop()
    #loop.run_until_complete(scan())

    loop.run_until_complete(connect(test_flag))

    if not test_flag:
        if rec_data.time != []:
            # Saving the Raw data (time, hr, rr)
            rec_data.save_raw_data(namefile)
