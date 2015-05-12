# coding: utf-8
__author__ = 'Joaquim Leitão'

# Imports to be used in the code
import timeit
import time
import numpy
import daqmxlib

actuator = daqmxlib.Actuator(["ao0", "ao1"])
reader = daqmxlib.Reader({"ai0": 1, "ai1": 1, "ai2": 1})

# Time Series Data
duration = 1800  # Seconds
times = numpy.array([0, 0.43, 0.45, 0.58, 0.6, 0.73, 0.75, 0.88, 0.9, 1.0]) * duration
# times = numpy.array([0, 774, 810, 1044, 1080, 1314, 1350, 1584, 1620, 1800])
levels_tank0 = numpy.array([0.3, 0.3, 0.55, 0.55, 0.3, 0.3, 0.55, 0.55, 0.3, 0.3])
levels_tank2 = numpy.array([0.25, 0.25, 0.45, 0.45, 0.25, 0.25, 0.45, 0.45, 0.25, 0.25])

print(times)

current_position = 0
number_events = len(times)

start_time = timeit.default_timer()

while current_position < number_events:
    current_time = timeit.default_timer()
    end_time = current_time - start_time

    # Find current position in the array and desired target
    current_position = numpy.where(times >= end_time)
    if len(current_position) == 0 or len(current_position[0]) == 0:
        break

    current_position = current_position[0][0]
    current_target_ai0 = levels_tank0[current_position]
    current_target_ai2 = levels_tank2[current_position]

    print "Elapsed Time: " + str(end_time) + " And position " + str(current_position)

    # Read and actuate
    tanks = reader.read_all(0.01, 1)
    current_value_ai0 = tanks["ai0"]
    current_value_ai2 = tanks["ai2"]

    if current_value_ai0 < current_target_ai0:
        print "Actuating " + str(0.005 * (current_target_ai0 - current_value_ai0))
        actuator.execute_task("ao0", 1, 0.005 * (current_target_ai0 - current_value_ai0))
    if current_value_ai2 < current_target_ai2:
        print "Actuating " + str(0.005 * (current_target_ai2 - current_value_ai2))
        actuator.execute_task("ao2", 1, 0.005 * (current_target_ai2 - current_value_ai2))

    # Sleep
    time_sleep = 1 - current_time - timeit.default_timer()
    if time_sleep > 0:
        time.sleep(time_sleep)