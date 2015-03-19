# coding: utf-8
#############################################################################################
#### The following code was based in the example available at
#### https://github.com/clade/PyDAQmx/blob/master/PyDAQmx/example/MultiChannelAnalogInput.py
#############################################################################################

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


class Reader():
    def __init__(self, physical_channel="[Dev1/ai1]", channel_name="", fs=1.0, samples=1):
        """Class Constructor"""
        # Get the set of physical channels from which we are going to extract the data
        if type(physical_channel) == type(""):
            self.physical_channel = [physical_channel]
        else:
            self.physical_channel = physical_channel
        self.physical_channel = list(set(self.physical_channel))  # Remove duplicates

        self.fs = fs  # Samples per second
        self.n_samples = samples  # Number of Samples to get at every callback
        self.data = numpy.zeros(self.n_samples)  # Store the data read at every callback

        # Create the tasks, one to read in each channel (But first create the task handles)
        # self.task_handles = dict([(channel, PyDAQmx.TaskHandle(0)) for channel in self.physical_channel])
        tasks = []
        for channel in self.physical_channel:
            task = PyDAQmx.Task()
            tasks.append(task)
            # Create Voltage Channel to read from the given physical channel
            task.CreateAIVoltageChan(channel, "", VAL_RSE, DAQMX_MIN_READER_V, DAQMX_MAX_READER_V, VAL_VOLTS, None)
        # Save all the tasks
        self.tasks = dict([(self.physical_channel[i], tasks[i]) for i in range(len(tasks))])


    def readAll(self):
    	"""Reads data from all the active physical channels
    	   Returns a dictionary with the data read from all the active physical channels"""
        return dict([(name, self.read(name)) for name in self.physical_channel])

    def read(self, name=None):
    	"""Reads data from a given physical channel
    	   Returns an array with the data read"""
        if name is None:
            name = self.physical_channel[0]

        # Get task handle        
        task_handle = self.tasks[name]
        # Prepare the data to be read
        data = numpy.zeros((1,), dtype=numpy.float64)
        # data = AI_data_type()
        read = PyDAQmx.int32()

        # Read the data and return it!
        PyDAQmx.Task.ReadAnalogF64(task_handle, 1, 10.0, GROUP_BY_CHANNEL, data, 1, PyDAQmx.byref(read), None)
        return data

    def start_task(self):
        """Starts the task, but does not start its execution"""
        self.StartTask()

    def stop_task(self):
        """Stops the task's execution and clears it"""
        self.StopTask()
        self.ClearTask()

    def DoneCallback(self, status):
        """Called when the task ends"""
        print "Status", status.value
        return 0  # The function should return an integer
