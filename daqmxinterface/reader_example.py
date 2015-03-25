# coding: utf-8
__author__ = 'Joaquim Leitão'

import daqmxlib

# Create a Reader Object, handling all the data acquisition operations from the different channels of the device.
# This constructor receives a dictionary as a parameter, specifying the channels used to obtain the data and the
# desired number of samples to collect from each channel
my_reader = daqmxlib.Reader({"Dev1/ai0": 5, "Dev1/ai1": 6})

# We can simply add a task by calling "add_task", specifying the desired channel and the number of samples to
# collect from that channel
my_reader.add_tasks({"Dev1/ai2": 10})

while True:
    # With read_all we can read the elements from all the specified channels
    print my_reader.read_all()