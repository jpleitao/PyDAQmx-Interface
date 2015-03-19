# coding: utf-8
__author__ = 'Joaquim Leitão'

import daqmxlib
import time

my_reader = daqmxlib.Reader("Dev1/ai1")

my_reader.start_all_tasks()
while True:
    print my_reader.read()
    time.sleep(1)

my_reader.stop_all_tasks()