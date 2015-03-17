# coding: utf-8
__author__ = 'Joaquim Leitão'

import PyDAQmx
import numpy

#  Constants definition
DAQMX_MIN_ACTUATION_V = 0.0
DAQMX_MAX_ACTUATION_V = 5.0
DAQMX_MIN_READER_V = -10.0
DAQMX_MAX_READER_V = 10.0
VAL_VOLTS = PyDAQmx.DAQmx_Val_Volts
GROUP_BY_CHANNEL = PyDAQmx.DAQmx_Val_GroupByChannel
GROUP_BY_SCAN_NUMBER = PyDAQmx.DAQmx_Val_GroupByScanNumber
VAL_RISING = PyDAQmx.DAQmx_Val_Rising
VAL_CONT_SAMPS = PyDAQmx.DAQmx_Val_ContSamps
VAL_RSE = PyDAQmx.DAQmx_Val_RSE
VAL_ACQUIRED_INTO_BUFFER = PyDAQmx.DAQmx_Val_Acquired_Into_Buffer


class Actuator(PyDAQmx.Task):
    def __init__(self, physical_channel="Dev1/ao0", channel_name=""):
        """Class Constructor"""
        PyDAQmx.Task.__init__(self)  # Call PyDAQmx.Task's constructor
        self.CreateAOVoltageChan(physical_channel, channel_name, DAQMX_MIN_ACTUATION_V, DAQMX_MAX_ACTUATION_V,
                                 VAL_VOLTS, None)  # Create Voltage Channel

    def start_task(self):
        """Starts the task, but does not start its execution"""
        self.StartTask()

    def stop_task(self):
        """Stops the task's execution"""
        self.StopTask()

    def clear_task(self):
        """Clears the task"""
        self.ClearTask()

    def execute_task(self, num_samps_channel, message, auto_start=1, timeout=0):
        """Executes the given task, starting its actuation"""
        self.WriteAnalogF64(num_samps_channel, auto_start, timeout, GROUP_BY_CHANNEL, message, None,
                            None)


#  class Reader(PyDAQmx.Task):
class Reader():
    def __init__(self, physical_channel="Dev1/ai1", channel_name="", fs=100.0, samples=1):
        """Class Constructor"""
        #  PyDAQmx.Task.__init__(self)  # Call PyDAQmx.Task's constructor
        self.fs = fs  # Samples per second
        self.n_samples = samples  # Number of Samples to get at every callback
        self.data = numpy.zeros(self.n_samples)  # Store the data read at every callback

        
        if type(physicalChannel) == type(""): # String type
            self.physicalChannel = [physicalChannel]
        else:
            self.physicalChannel = physicalChannel
        
        taskHandles = dict([(channel,PyDAQmx.TaskHandle(0)) for channel in self.physicalChannel])
        
        for channel in self.physical_channel:
            PyDAQmx.DAQmxCreateTask("",byref(taskHandles[channel]))
            PyDAQmx.DAQmxCreateAIVoltageChan(taskHandles[channel], channel, channel_name, VAL_RSE, DAQMX_MIN_READER_V, DAQMX_MAX_READER_V,
                                     VAL_VOLTS, None)  # Create Voltage Channel

        self.task_handles = taskHandles

        
        # Sets the source of the Sample Clock to self.fs with a rate equal to "VAL_RISING" and the number of samples to
        # acquire or generate set to self.n_samples
        self.CfgSampClkTiming("", self.fs, VAL_RISING, VAL_CONT_SAMPS, self.n_samples)
        # Register the callback method "EveryNCallback" (default) to receive an event when self.n_samples samples have
        # been written from the device to the buffer
        self.AutoRegisterEveryNSamplesEvent(VAL_ACQUIRED_INTO_BUFFER, self.n_samples, 0)
        self.AutoRegisterDoneEvent(0)

    def start_tasks(self):
        """Starts the task, but does not start its execution"""
        #  Percorrer todas as tasks e fazer start task
        self.StartTask()

    def stop_tasks(self):
        """Stops the task's execution"""
        #  Percorrer todas as tasks e fazer stop task
        self.StopTask()

    def clear_tasks(self):
        """Clears the task"""
        #  Percorrer todas as tasks e fazer clear task
        self.ClearTask()

    def EveryNCallback(self, timeout=0):
        """Default method called when a specified number of samples have been written from the device to the buffer"""
        read = PyDAQmx.int32()

        for current_task in self.task_handles:
            # Reads self.n_samples floating-point samples to the array "self.data" of "self.n_samples" samples
            PyDAQmx.DAQmxReadAnalogF64(current_task, self.n_samples, timeout, GROUP_BY_SCAN_NUMBER, self.data, self.n_samples,
                                       PyDAQmx.byref(read), None)
        print self.data
        return 0  # The function should return an integer

    def DoneCallback(self, status):
        """Called when the task ends"""
        print "Status", status.value
        return 0  # The function should return an integer
