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
# duration = 300
times = numpy.array([0, 0.43, 0.45, 0.58, 0.6, 0.73, 0.75, 0.88, 0.9, 1.0]) * duration
# times = numpy.array([0, 774, 810, 1044, 1080, 1314, 1350, 1584, 1620, 1800])
# levels_tank0 = numpy.array([0.3, 0.3, 0.55, 0.55, 0.3, 0.3, 0.55, 0.55, 0.3, 0.3])
levels_tank0 = numpy.array([0.33, 0.33, 0.58, 0.58, 0.33, 0.33, 0.58, 0.58, 0.33, 0.33])
# levels_tank2 = numpy.array([0.25, 0.25, 0.45, 0.45, 0.25, 0.25, 0.45, 0.45, 0.25, 0.25])
levels_tank2 = numpy.array([0.28, 0.28, 0.48, 0.48, 0.28, 0.28, 0.48, 0.48, 0.28, 0.28])

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

    # Read and convert from volts to meters
    tanks = reader.read_all()
    current_value_ai0 = (0.6 / -16.7) * (tanks["ai0"][0] - 10)  # meters
    current_value_ai1 = (0.6 / -16.7) * (tanks["ai1"][0] - 10)  # meters

    print "Read " + str(current_value_ai0) + " and expected " + str(current_target_ai0)
    print "Read " + str(current_value_ai1) + " and expected " + str(current_target_ai2)

    actuation = 40 * (current_target_ai0 - current_value_ai0)
    result = actuator.execute_task("ao0", 1, actuation)
    print "Actuated " + str(actuation) + " " + str(result)
    actuation = 40 * (current_target_ai2 - current_value_ai1)
    result = actuator.execute_task("ao1", 1, actuation)
    print "Actuated " + str(actuation) + " " + str(result)

    # Sleep
    time_sleep = 1 - (current_time - timeit.default_timer())
    print time_sleep
    if time_sleep > 0:
        time.sleep(time_sleep)

actuator.execute_task("ao0", 1, 0)
actuator.execute_task("ao1", 1, 0)