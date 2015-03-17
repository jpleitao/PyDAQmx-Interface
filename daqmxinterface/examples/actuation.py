# coding: utf-8
__author__ = 'Joaquim Leitão'

import PyDAQmx
import numpy

analog_output = PyDAQmx.Task()

# DAQmx Configure Code
analog_output.CreateAOVoltageChan("Dev1/ao0", "", 0, 5.0, PyDAQmx.DAQmx_Val_Volts,
                                  None)

print "Task Created"

# DAQmx Start Code
analog_output.StartTask()

print "Task Started"

import time

x = [i for i in range(100)]
data = [numpy.abs(numpy.sin(i)) for i in x]
# data = numpy.array([5.0, 2.0])
print data

for banana in data:
    data2 = numpy.array(banana)
    analog_output.WriteAnalogF64(1, 1, 0, PyDAQmx.DAQmx_Val_GroupByChannel, data2, None, None)
    time.sleep(3)
    print("Going to run")

