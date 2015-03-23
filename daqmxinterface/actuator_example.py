# coding: utf-8
__author__ = 'Joaquim Leitão'

import daqmxlib
import numpy
import time

my_actuator = daqmxlib.Actuator("Dev1/ao0")

x = [i for i in range(3)]
data = [numpy.abs(numpy.sin(i)) for i in x]
# data = numpy.array([5.0, 2.0])
print data

for current in data:
    data2 = numpy.array(current)
    my_actuator.execute_task("Dev1/ao0", 1, data2)
    print("Executing task...")
    time.sleep(3)

print("Stopping and Clearing Task...")
my_actuator.stop_task("Dev1/ao0")