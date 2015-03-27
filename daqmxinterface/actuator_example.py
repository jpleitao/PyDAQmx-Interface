# coding: utf-8
__author__ = 'Joaquim Leitão'

import daqmxlib
import math
import time

my_actuator = daqmxlib.Actuator(["ao1"])

x = [i for i in range(10)]
data = [abs(math.sin(i)) for i in x]
print data

for current in data:
    print "Executing task... " + str(my_actuator.execute_task("ao1", 1, current)) + "!"
    time.sleep(1)