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
VAL_FINITE_SAMPS = PyDAQmx.DAQmx_Val_FiniteSamps
VAL_RSE = PyDAQmx.DAQmx_Val_RSE
VAL_ACQUIRED_INTO_BUFFER = PyDAQmx.DAQmx_Val_Acquired_Into_Buffer


class Actuator():
    """
    Actuator class, responsible for actuating in a given channel of the NI-USB Data Acquisition Hardware
    """

    def __init__(self, physical_channels=["ao0"]):
        """
        Class Constructor
        :param physical_channels: A list of physical channels used to acquire the data
        """
        # Check for argument's type
        if not isinstance(physical_channels, list) and not isinstance(physical_channels, str):
            raise TypeError("Wrong type for argument channels_samples: Expected <class 'dict'> or <class 'str'> "
                            "and found " + str(type(physical_channels)))

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
            task.CreateAOVoltageChan("Dev1/" + str(channel), "", DAQMX_MIN_ACTUATION_V, DAQMX_MAX_ACTUATION_V,
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
        :param message: The message to send to the actuator
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
        # TODO: CHANGE "name" TO BE A LIST: FUNCTION SHOULD ALSO CHANGE NAME

        # Message has to be a numpy array, so lets convert it to the desired data type
        message = numpy.array(message)

        # Check for the limits of the message
        message[message > DAQMX_MAX_ACTUATION_V] = DAQMX_MAX_ACTUATION_V
        message[message < DAQMX_MIN_ACTUATION_V] = DAQMX_MIN_ACTUATION_V

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

    def __init__(self, channels_samples={"ai1": 1}):
        """
        Class Constructor
        :param channels_samples: A dictionary with a mapping between the physical channels used to acquire the data and
                                 the number of samples to collect from each one of them
        """
        # Check for argument's type
        if not isinstance(channels_samples, dict):
            raise TypeError("Wrong type for argument channels_samples: Expected <class 'dict'> and found " +
                            str(type(channels_samples)))

        # Get the set of physical channels from which we are going to extract the data and do the same for the names of
        # the channels
        self.physical_channels = list(channels_samples.keys())
        self.n_samples = []

        tasks = []
        for channel in self.physical_channels:
            current_samples = channels_samples[channel]
            # Store the number of samples to read from that channel
            self.n_samples.append(current_samples)
            # Create the tasks, one to read in each channel
            task = PyDAQmx.Task()
            # Create Voltage Channel to read from the given physical channel
            task.CreateAIVoltageChan("Dev1/" + str(channel), "", VAL_RSE, DAQMX_MIN_READER_V, DAQMX_MAX_READER_V, VAL_VOLTS,
                                     None)
            # Set the source of the sample clock - Acquire infinite number of samples and enabling to read the maximum
            # number of samples per second: 10000.0
            task.CfgSampClkTiming("", 10000.0, VAL_RISING, VAL_CONT_SAMPS, current_samples)
            # Add the task to the list of tasks
            tasks.append(task)
        # Save all the tasks
        self.tasks = dict([(self.physical_channels[i], tasks[i]) for i in range(len(tasks))])

    def start_tasks(self):
        for current in self.tasks.keys():
            task = self.tasks[current]
            task.StartTask()

    def change_collected_samples(self, channel, number_samples):
        """
        Changes the number of samples collected in the specified physical channel
        :param channel: The desired physical channel
        :param number_samples: The new number of samples to collect
        """

        if channel in self.physical_channels:
            # Create a new task for the given channel that is going to
            task = PyDAQmx.Task()
            task.CreateAIVoltageChan("Dev1/" + str(channel), "", VAL_RSE, DAQMX_MIN_READER_V, DAQMX_MAX_READER_V,
                                     VAL_VOLTS, None)
            # Set the source of the sample clock - Acquire infinite number of samples and enabling to read the maximum
            # number of samples per second: 10000.0
            task.CfgSampClkTiming("", 10000.0, VAL_RISING, VAL_CONT_SAMPS, number_samples)
            self.tasks[channel] = task

            index = self.physical_channels.index(channel)
            self.n_samples[index] = number_samples

            return True
        else:
            raise TypeError("Attempt to change number of collected samples from a physical channel not already added")

    def add_tasks(self, channel_samples):
        """
        Adds a task to the set of tasks
        :param channel_samples: A dictionary with a mapping between the physical channels used to acquire the data and
                                the number of samples to collect from each one of them
        """
        # Check for argument's type
        if not isinstance(channel_samples, dict):
            raise TypeError("Wrong type for argument channels_samples: Expected <class 'dict'> and found " +
                            str(type(channel_samples)))

        # Get the list of channels
        physical_channels = list(channel_samples.keys())

        for channel in physical_channels:
            current_samples = channel_samples[channel]
            # Update the list of physical channels
            self.physical_channels.append(channel)
            # Store the number of samples to collect for each of the given channels
            self.n_samples.append(current_samples)
            # Create a task and the voltage channel and store it
            task = PyDAQmx.Task()
            task.CreateAIVoltageChan("Dev1/" + str(channel), "", VAL_RSE, DAQMX_MIN_READER_V, DAQMX_MAX_READER_V,
                                     VAL_VOLTS, None)
            # Set the source of the sample clock - Acquire infinite number of samples and enabling to read the maximum
            # number of samples per second: 10000.0
            task.CfgSampClkTiming("", 10000.0, VAL_RISING, VAL_CONT_SAMPS, current_samples)
            self.tasks[channel] = task

    def remove_task(self, physical_channel):
        """
        Removes a given Task from the set of active Tasks
        :param physical_channel: The task to remove
        :return: True in case of success, otherwise returns False
        """
        # Check if the given physical channel is in the list of physical channels
        if physical_channel in self.physical_channels:
            # Get the index of the given physical channel in the list of physical channels
            index = self.physical_channels.index(physical_channel)
            # Remove the element from the list of physical channels
            self.physical_channels.remove(physical_channel)
            # Remove the number of samples associated with the given channel
            self.n_samples.remove(self.n_samples[index])

        # Remove the task
        del self.tasks[physical_channel]

        return True

    def read_all(self, timeout=0.01, num_samples=None):
        """
        Reads data from all the active physical channels
        :param timeout: The amount of time, in seconds, to wait for the function to read the sample(s)
                        (-1 for infinite)
        :param num_samples: A list with the number of samples to acquire for each channel
        :return: Returns a dictionary with the data read from all the active physical channels
        """

        if num_samples is None:
            return dict([(name, self.read(name, timeout)) for name in self.physical_channels])
        elif not isinstance(num_samples, dict):
            raise TypeError("Wrong type for argument num_samples: Expected <class 'dict'> and found " +
                            str(type(num_samples)))

        contents = {}
        for name in self.physical_channels:
            current_number_samples = num_samples[name]
            contents[name] = self.read(name, timeout, current_number_samples)
        return contents

    def read(self, name=None, timeout=0.01, num_samples=None):
        """
        Reads data from a given physical channel
        :param name: The name of the channel from which we are going to read the data
        :param timeout: The amount of time, in seconds, to wait for the function to read the sample(s)
                        (-1 for infinite)
        :param num_samples: The number of samples to acquire
        :return: Returns an array with the data read
        """
        if name is None:
            name = self.physical_channels[0]
        if num_samples is None:
            index = self.physical_channels.index(name)
            num_samps_channel = self.n_samples[index]
        else:
            num_samps_channel = num_samples

        # Get task handle
        task = self.tasks[name]
        # Prepare the data to be read
        data = numpy.zeros((num_samps_channel,), dtype=numpy.float64)
        read = PyDAQmx.int32()
        # Start the task
        task.StartTask()
        # Read the data and return it!
        task.ReadAnalogF64(num_samps_channel, timeout, GROUP_BY_CHANNEL, data, num_samps_channel,
                           PyDAQmx.byref(read), None)
        # Stop the task
        task.StopTask()
        # Return in a list instead of numpy.array
        return data.tolist()