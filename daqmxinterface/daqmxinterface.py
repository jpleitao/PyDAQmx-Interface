# coding: utf-8
__author__ = 'Joaquim Leitão'

import PyDAQmx

#  Define constants of the library
DAQMX_MIN_ACTUATION_V = 0.0
DAQMX_MAX_ACTUATION_V = 5.0


class Actuator(PyDAQmx.Task):
    def __init__(self, physical_channel="Dev1/ao0", channel_name=""):
        PyDAQmx.Task.__init__(self)  # Call PyDAQmx.Task's constructor
        self.CreateAOVoltageChan(physical_channel, channel_name, DAQMX_MIN_ACTUATION_V, DAQMX_MAX_ACTUATION_V,
                                 PyDAQmx.DAQmx_Val_Volts, None)

    def start_task(self):
        self.StartTask()

    def execute_task(self, num_samps_channel, message, auto_start=1, timeout=0):
        self.WriteAnalogF64(num_samps_channel, auto_start, timeout, PyDAQmx.DAQmx_Val_GroupByChannel, message, None,
                            None)