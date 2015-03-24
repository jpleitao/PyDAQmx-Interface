# coding: utf-8
__author__ = 'Joaquim Leitão'

import daqmxlib
import time

# Create a Reader Object, handling all the data acquisition operations from the different channels of the device.
# This constructor receives a dictionary as a parameter, specifying the channels used to obtain the data and the
# desired number of samples to collect from each channel (Until further notice this number should stay 1 due to
# problems in the PyDAQmx library to collect more than one element)
my_reader = daqmxlib.Reader({"Dev1/ai1": 1, "Dev1/ai3": 1})

# We can simply add a task by calling "add_task", specifying the desired channel and the number of samples to
# collect from that channel
my_reader.add_tasks({"Dev1/ai2": 1})

while True:
    # With read_all we can read the elements from all the specified channels
    print my_reader.read_all()
    time.sleep(1)