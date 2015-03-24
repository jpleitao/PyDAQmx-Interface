# coding: utf-8
__author__ = 'Joaquim Leitão'

import daqmxlib
import time

my_reader = daqmxlib.Reader({"Dev1/ai1": 2, })

my_reader.add_tasks({"Dev1/ai2": 4})

while True:
    print my_reader.read_all()
    time.sleep(1)