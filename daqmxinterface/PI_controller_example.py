# coding: utf-8
from datetime import datetime
import time
import traceback
import daqmxlib

__author__ = 'Joaquim Leitão'

Kp = 1.2
r = 5
fs = 0.05 # IN SECONDS
total = 480 # IN SECONDS
my_reader = daqmxlib.Reader({"ai0": 1})
my_actuator = daqmxlib.Actuator(["ao1"])
y = my_reader.read_all()['ai0'][0]
start = datetime.now()
for i in range(int(total/fs)):
    tic = datetime.now()
    try:
        y = my_reader.read_all()['ai0'][0]
        pass
    except Exception:
        traceback.print_exc()
        pass
    u = Kp * r - Kp * y
    my_actuator.execute_task("ao1", 1, u)
    duration = (datetime.now() - tic).total_seconds()
    remaining = fs - duration
    if remaining < 0:
        print "Failed", remaining
        exit(1)
    print str(i) + " " + str(duration) + " " + str(remaining) + " " + str(remaining + duration) + " " + str(u)
    time.sleep(remaining)

print "Ended in: ", (datetime.now() - start).total_seconds(), " Seconds"