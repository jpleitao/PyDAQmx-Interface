# coding: utf-8
#############################################################################################
# The following code was based in the example available at
# https://github.com/clade/PyDAQmx/blob/master/PyDAQmx/example/MultiChannelAnalogInput.py
#############################################################################################

__author__ = 'Joaquim Leitão'

import PyDAQmx
import numpy

# Constants definition
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


class Actuator():
    """
    Actuator class, responsible for actuating in a given channel of the NI-USB Data Acquisition Hardware
    """
    def __init__(self, physical_channels=["Dev1/ao0"]):
        """
        Class Constructor
        :param physical_channels: A list of physical channels used to acquire the data
        """

        # Get the set of physical channels from which we are going to extract the data and do the same for the names of
        # the channels
        self.physical_channels = self.__parse(physical_channels)
        self.physical_channels = list(set(self.physical_channels))  # Remove duplicates

        # Create tasks, one for each physical channel
        tasks = []
        for i in range(len(self.physical_channels)):
            channel = self.physical_channels[i]
            task = PyDAQmx.Task()
            tasks.append(task)
            # Create Voltage Channel to read from the given physical channel
            task.CreateAOVoltageChan(channel, "", DAQMX_MIN_ACTUATION_V, DAQMX_MAX_ACTUATION_V,
                                     VAL_VOLTS, None)  # Create Voltage Channel
        # Save all the tasks
        self.tasks = dict([(self.physical_channels[i], tasks[i]) for i in range(len(tasks))])

    @staticmethod
    def __parse(data):
        """
        Private Method that parses a list or a string containing either a set of physical_channels or a set of channel's
        names into a list
        :param data: The mentioned list or string
        :return: The parsed data in the list format
        """
        if isinstance(data, str):
            return [data]

        return data

    def execute_all_tasks(self, num_samps_channel, message, auto_start=1, timeout=0):
        """
        Executes all the tasks created. Ideally this should be use to send the same message to a set of actuators
        :param num_samps_channel: The number of samples, per channel, to write
        :param message: he message to send to the actuator
        :param auto_start: Specifies whether or not this function automatically starts the task if you do not start it.
        :param timeout:The amount of time, in seconds, to wait for this function to write all the samples
                        (-1 for inifinite)
        :return: A boolean value: True is all the tasks started without major problems; False otherwise
        """
        for name in self.physical_channels:
            result = self.execute_task(name, num_samps_channel, message, auto_start, timeout)
            if not result:
                return False
        return True

    def execute_task(self, name, num_samps_channel, message, auto_start=1, timeout=0):
        """
        Executes a given task, starting its actuation (That is, sends a given message to a given actuator)
        :param name: The name of the task to execute
        :param num_samps_channel: The number of samples, per channel, to write
        :param message: The message to send to the actuator
        :param auto_start: Specifies whether or not this function automatically starts the task if you do not start it.
        :param timeout: The amount of time, in seconds, to wait for this function to write all the samples
                        (-1 for inifinite)
        :return: A boolean value, indicating the success or failure of the execution
        """
        if name in self.tasks.keys():
            # Get the task
            task = self.tasks[name]
            # Start the task
            task.StartTask()
            # Write to buffer
            task.WriteAnalogF64(num_samps_channel, auto_start, timeout, GROUP_BY_CHANNEL, message, None,
                                None)
            task.StopTask()
            return True
        return False


class Reader():
    """
    Reader class, responsible for collecting data from the NI-USB Data Acquisition Hardware
    """
    def __init__(self, physical_channels=["Dev1/ai1"], samples=1):
        """
        Class Constructor
        :param physical_channels: A list of physical channels used to acquire the data
        :param samples: The number of samples to collect
        """
        # Get the set of physical channels from which we are going to extract the data and do the same for the names of
        # the channels
        self.physical_channels = self.__parse_channels(physical_channels)
        self.physical_channels = list(set(self.physical_channels))  # Remove duplicates

        # FIXME: Implement this with a list of samples per channel -- Could receive a dictionary!
        self.n_samples = samples

        # Create the tasks, one to read in each channel (But first create the task handles)
        tasks = []
        for i in range(len(self.physical_channels)):
            channel = self.physical_channels[i]
            task = PyDAQmx.Task()
            tasks.append(task)
            # Create Voltage Channel to read from the given physical channel
            task.CreateAIVoltageChan(channel, "", VAL_RSE, DAQMX_MIN_READER_V, DAQMX_MAX_READER_V, VAL_VOLTS,
                                     None)
        # Save all the tasks
        self.tasks = dict([(self.physical_channels[i], tasks[i]) for i in range(len(tasks))])

    @staticmethod
    def __parse_channels(data):
        """
        Private Method that parses a list or a string containing either a set of physical_channels or a set of channel's
        names into a list
        :param data: The mentioned list or string
        :return: The parsed data in the list format
        """
        if isinstance(data, str):
            return [data]

        return data

    def add_task(self, physical_channel):
        """
        Adds a task to the set of tasks
        :param physical_channel: The physical channel where the data will be collected
        """
        # Create a task and a handle for the task
        task = PyDAQmx.Task()
        task.CreateAIVoltageChan(physical_channel, "", VAL_RSE, DAQMX_MIN_READER_V, DAQMX_MAX_READER_V,
                                 VAL_VOLTS, None)

        self.tasks[physical_channel] = task
        self.physical_channels.append(physical_channel)

    def remove_task(self, physical_channel):
        """
        Removes a given Task from the set of active Tasks
        :param physical_channel:
        :return: True in case of success, otherwise returns False
        """

        # Stop current task
        if not self.stop_task(physical_channel):
            return False

        # Remove the task and the task handle
        del self.tasks[physical_channel]

        return True

    def read_all(self):
        """
        Reads data from all the active physical channels
        :return: Returns a dictionary with the data read from all the active physical channels
        """
        return dict([(name, self.read(name)) for name in self.physical_channels])

    def read(self, name=None):
        """
        Reads data from a given physical channel
        :param name: The name of the channel from which we are going to read the data
        :return: Returns an array with the data read
        """

        # TODO: SHOULD AVOID REPETITIVE READS

        if name is None:
            name = self.physical_channels[0]

        # Get task handle        
        task = self.tasks[name]
        # Prepare the data to be read
        data = numpy.zeros((self.n_samples,), dtype=numpy.float64)
        # data = AI_data_type()
        read = PyDAQmx.int32()
        # Start the task
        task.StartTask()
        # Read the data and return it!
        PyDAQmx.Task.ReadAnalogF64(task, 1, 10.0, GROUP_BY_CHANNEL, data, 1, PyDAQmx.byref(read), None)
        # Stop the current task
        task.StopTask()
        return data