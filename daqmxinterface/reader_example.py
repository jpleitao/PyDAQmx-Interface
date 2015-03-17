# coding: utf-8
__author__ = 'Joaquim Leitão'

import daqmxlib

my_reader = daqmxlib.Reader("Dev1/ai1")
my_reader.start_task()

raw_input('Acquiring samples continuously. Press Enter to interrupt\n')
my_reader.stop_task()
my_reader.clear_task()