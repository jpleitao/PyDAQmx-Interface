# coding: utf-8

import numpy
import PyDAQmx


class MultiChannelAnalogInput():
    """Class to create a multi-channel analog input

    Usage: AI = MultiChannelInput(physicalChannel)
        physicalChannel: a string or a list of strings
    optional parameter: limit: tuple or list of tuples, the AI limit values
                        reset: Boolean
    Methods:
        read(name), return the value of the input name
        readAll(), return a dictionary name:value
    """

    def __init__(self, physical_channel, limit=None, reset=False):
        if type(physical_channel) == type(""):
            self.physicalChannel = [physical_channel]
        else:
            self.physicalChannel = physical_channel
        self.numberOfChannel = physical_channel.__len__()
        if limit is None:
            self.limit = dict([(name, (-10.0, 10.0)) for name in self.physicalChannel])
        elif type(limit) == tuple:
            self.limit = dict([(name, limit) for name in self.physicalChannel])
        else:
            self.limit = dict([(name, limit[i]) for i, name in enumerate(self.physicalChannel)])
        if reset:
            PyDAQmx.DAQmxResetDevice(physical_channel[0].split('/')[0])

        self.task_handles = []

    def configure(self):
        # Create one task handle per Channel
        task_handles = dict([(name, PyDAQmx.TaskHandle(0)) for name in self.physicalChannel])
        tasks = []
        for name in self.physicalChannel:
            task = PyDAQmx.Task()
            tasks.append(task)
            # PyDAQmx.DAQmxCreateTask("", PyDAQmx.byref(task_handles[name]))
            task.CreateAIVoltageChan(name, "", PyDAQmx.DAQmx_Val_RSE,
                                     self.limit[name][0], self.limit[name][1],
                                     PyDAQmx.DAQmx_Val_Volts, None)  # Can replace limits with my own limits
        self.task_handles = task_handles
        self.tasks = dict([(self.physicalChannel[i], tasks[i]) for i in range(len(tasks))])

    def readAll(self):
        return dict([(name, self.read(name)) for name in self.physicalChannel])

    def read(self, name=None):
        if name is None:
            name = self.physicalChannel[0]
        task_handle = self.task_handles[name]
        task_handle = self.tasks[name]
        PyDAQmx.Task.StartTask(task_handle)
        data = numpy.zeros((1,), dtype=numpy.float64)
        # data = AI_data_type()
        read = PyDAQmx.int32()
        PyDAQmx.Task.ReadAnalogF64(task_handle, 1, 10.0, PyDAQmx.DAQmx_Val_GroupByChannel, data, 1,
                                   PyDAQmx.byref(read), None)
        PyDAQmx.Task.StopTask(task_handle)
        return data[0]


if __name__ == '__main__':
    import time

    multipleAI = MultiChannelAnalogInput(["Dev1/ai2", "Dev1/ai1"])
    multipleAI.configure()

    while True:
        print multipleAI.readAll()
        time.sleep(1)
