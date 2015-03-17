# coding: utf-8
__author__ = 'Joaquim Leitão'

from PyDAQmx import Task
from numpy import zeros
import PyDAQmx

"""This example is a PyDAQmx version of the ContAcq_IntClk.c example
It illustrates the use of callback functions

This example demonstrates how to acquire a continuous amount of
data using the DAQ device's internal clock. It incrementally stores the data
in a Python list.
"""

# minimo= -5.5 V


class CallbackTask(Task):
    def __init__(self):
        Task.__init__(self)
        self.a = []
        self.Fs = 100.0  # Samples per second
        self.nSamples = 1
        self.data = zeros(self.nSamples)
        self.CreateAIVoltageChan("Dev1/ai1", "", PyDAQmx.DAQmx_Val_RSE, -10.0, 10.0, PyDAQmx.DAQmx_Val_Volts, None)
        self.CfgSampClkTiming("", self.Fs, PyDAQmx.DAQmx_Val_Rising, PyDAQmx.DAQmx_Val_ContSamps, self.nSamples)
        self.AutoRegisterEveryNSamplesEvent(PyDAQmx.DAQmx_Val_Acquired_Into_Buffer, self.nSamples, 0)
        self.AutoRegisterDoneEvent(0)

    def EveryNCallback(self):
        read = PyDAQmx.int32()
        self.ReadAnalogF64(self.nSamples, 0, PyDAQmx.DAQmx_Val_GroupByScanNumber, self.data, self.nSamples,
                           PyDAQmx.byref(read), None)
        self.a.extend(self.data.tolist())
        print self.data
        return 0  # The function should return an integer

    def DoneCallback(self, status):
        print "Status", status.value
        return 0  # The function should return an integer


task = CallbackTask()
task.StartTask()

raw_input('Acquiring samples continuously. Press Enter to interrupt\n')

task.StopTask()
task.ClearTask()