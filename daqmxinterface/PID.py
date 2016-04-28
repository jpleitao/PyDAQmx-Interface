#!/usr/bin/python
#
# This file is part of IvPID.
# Copyright (C) 2015 Ivmech Mechatronics Ltd. <bilgi@ivmech.com>
#
# IvPID is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IvPID is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# title           :PID.py
# description     :python pid controller
# author          :Caner Durmusoglu
# date            :20151218
# version         :0.1
# notes           :
# python_version  :2.7
# ==============================================================================

"""Ivmech PID Controller is simple implementation of a Proportional-Integral-Derivative (PID) Controller at Python Programming Language.
More information about PID Controller: http://en.wikipedia.org/wiki/PID_controller
"""
import threading
import time
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import spline
import daqmxlib


class PID:
    """PID Controller
    """

    def __init__(self, P=0.2, I=0.0, D=0.0):

        self.Kp = P
        self.Ki = I
        self.Kd = D

        self.sample_time = 0.00
        self.current_time = time.time()
        self.last_time = self.current_time

        self.clear()

    def clear(self):
        """Clears PID computations and coefficients"""
        self.SetPoint = 0.0

        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0

        # Windup Guard
        self.int_error = 0.0
        self.windup_guard = 20.0

        self.output = 0.0

    def update(self, feedback_value):
        """Calculates PID value for given reference feedback

        .. math::
            u(t) = K_p e(t) + K_i \int_{0}^{t} e(t)dt + K_d {de}/{dt}

        .. figure:: images/pid_1.png
           :align:   center

           Test PID with Kp=1.2, Ki=1, Kd=0.001 (test_pid.py)

        """
        error = self.SetPoint - feedback_value
        print self.SetPoint, feedback_value, error

        self.current_time = time.time()
        delta_time = self.current_time - self.last_time
        delta_error = error - self.last_error

        if (delta_time >= self.sample_time):
            self.PTerm = self.Kp * error
            self.ITerm += error * delta_time

            if (self.ITerm < -self.windup_guard):
                self.ITerm = -self.windup_guard
            elif (self.ITerm > self.windup_guard):
                self.ITerm = self.windup_guard

            self.DTerm = 0.0
            if delta_time > 0:
                self.DTerm = delta_error / delta_time

            # Remember last time and last error for next calculation
            self.last_time = self.current_time
            self.last_error = error

            self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)

    def setKp(self, proportional_gain):
        """Determines how aggressively the PID reacts to the current error with setting Proportional Gain"""
        self.Kp = proportional_gain

    def setKi(self, integral_gain):
        """Determines how aggressively the PID reacts to the current error with setting Integral Gain"""
        self.Ki = integral_gain

    def setKd(self, derivative_gain):
        """Determines how aggressively the PID reacts to the current error with setting Derivative Gain"""
        self.Kd = derivative_gain

    def setWindup(self, windup):
        """Integral windup, also known as integrator windup or reset windup,
        refers to the situation in a PID feedback controller where
        a large change in setpoint occurs (say a positive change)
        and the integral terms accumulates a significant error
        during the rise (windup), thus overshooting and continuing
        to increase as this accumulated error is unwound
        (offset by errors in the other direction).
        The specific problem is the excess overshooting.
        """
        self.windup_guard = windup

    def setSampleTime(self, sample_time):
        """PID that should be updated at a regular interval.
        Based on a pre-determined sampe time, the PID decides if it should compute or return immediately.
        """
        self.sample_time = sample_time


class ControllerThread(threading.Thread):
    def __init__(self, reader, controller, P=0.2, I=0.0, D=0.0, SETPOINT=1.0, FS=0.05, SAMPLES=100):
        threading.Thread.__init__(self)
        self.feedback_list = []
        self.setpoint_list = []
        self.output_list = []
        self.time_sm = []
        self.time_list = []
        self.P = P
        self.I = I
        self.D = D
        self.SAMPLES = SAMPLES
        self.FS = FS
        self.feedback_smooth = []
        self.reader = reader
        self.controller = controller
        self.SETPOINT = SETPOINT
        self.completed = False
        self.failed = {"status": False, "reason": ""}
        self.type = "PID"

    def run(self):
        pid = PID(self.P, self.I, self.D)

        pid.SetPoint = 0.0
        pid.setSampleTime(self.FS)

        END = self.SAMPLES

        for i in range(1, END):
            tic = datetime.now()
            feedback = self.reader.read_all()["ai0"][0]
            if feedback < 0:
                feedback = 0
            print "Feedback: ", feedback
            pid.update(feedback)
            u = pid.output
            # print "Output: ", u
            self.controller.execute_task("ao0", 1, u)

            if i > 9:
                pid.SetPoint = self.SETPOINT

            duration = (datetime.now() - tic).total_seconds()
            remaining = self.FS - duration
            print str(i) + " " + str(duration) + " " + str(remaining) + " " + str(remaining + duration), feedback, u
            if remaining < 0:
                self.failed["status"] = True
                self.failed["reason"] = "Sampling frequency is too big."
                exit(1)
            time.sleep(remaining)

            self.feedback_list.append(feedback)
            self.output_list.append(u)
            self.setpoint_list.append(pid.SetPoint)
            self.time_list.append(i)

        self.time_sm = np.array(self.time_list)
        self.time_smooth = np.linspace(self.time_sm.min(), self.time_sm.max(), 300)
        self.feedback_smooth = spline(self.time_list, self.feedback_list, self.time_smooth)
        self.output_smooth = spline(self.time_list, self.output_list, self.time_smooth)
        self.completed = True


if __name__ == "__main__":
    SAMPLES = 10
    my_reader = daqmxlib.Reader({"ai0": 1})
    my_actuator = daqmxlib.Actuator(["ao0"])
    my_actuator.execute_task("ao0", 1, 0)
    time.sleep(1)
    controller_thread = ControllerThread(my_reader, my_actuator, P=2, I=1, D=0, SETPOINT=3, FS=0.05, SAMPLES=SAMPLES)
    controller_thread.start()
    controller_thread.join()
    # print controller_thread.feedback_smooth

    if controller_thread.completed:
        plt.plot(controller_thread.time_smooth, controller_thread.feedback_smooth)
        plt.plot(controller_thread.time_smooth, controller_thread.output_smooth)
        plt.plot(controller_thread.time_list, controller_thread.setpoint_list)
        plt.xlim((0, SAMPLES))
        plt.ylim(-10, 10)
        # plt.ylim((min(controller_thread.feedback_list) - 0.5, max(controller_thread.feedback_list) + 0.5))
        plt.xlabel('time (s)')
        plt.ylabel('PID (PV)')
        plt.title('TEST PID')

        plt.grid(True)
        plt.show()
