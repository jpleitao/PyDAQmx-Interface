# coding: utf-8
__author__ = 'Joaquim Leitão'

import daqmxlib
import math
import time

my_actuator = daqmxlib.Actuator(["Dev1/ao1"])

x = [i for i in range(10)]
data = [abs(math.sin(i)) for i in x]
print data

for current in data:
    my_actuator.execute_task("Dev1/ao0", 1, current)
    print("Executing task...")
    time.sleep(1)