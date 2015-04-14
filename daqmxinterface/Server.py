# coding: utf-8
__author__ = 'Joaquim Leitão'

# System imports
import time
import traceback
import sys
import threading
import Pyro4

# Import daqmxlib and other private libraries
import daqmxlib
import utils

TIMER_STEP = 1.0
LIMIT_FAILS = 10
global MIN_READ_VALUE
global MAX_READ_VALUE
global can_actuate_ao0
global can_actuate_ao1
MIN_READ_VALUE = -6
MAX_READ_VALUE = -5
can_actuate_ao0 = True
can_actuate_ao1 = True


def check_board(board):
    global MIN_READ_VALUE
    global can_actuate_ao0
    global can_actuate_ao1

    while True:
        try:
            readings = board.read_all()

            readings_ai0 = readings['ai0']
            readings_ai1 = readings['ai1']

            readings_ai0 = readings_ai0[0]
            readings_ai1 = readings_ai1[0]

            print "Read " + str(readings_ai0) + " and " + str(readings_ai1)

            if can_actuate_ao0 and readings_ai0 <= MIN_READ_VALUE:
                # Cannot actuate anymore in ai0
                print "Cannot actuate anymore in ai0"
                can_actuate_ao0 = False
                # Send 0 to ao0
                board.actuator.execute_task("ao0", 1, 0)
            elif (not can_actuate_ao0) and readings_ai0 >= MAX_READ_VALUE:
                # Can actuate back in ai0
                print "Can actuate back in ai0"
                can_actuate_ao0 = True

            if can_actuate_ao1 and readings_ai1 <= MIN_READ_VALUE:
                # Cannot actuate anymore in ai1
                print "Cannot actuate anymore in ai1"
                can_actuate_ao1 = False
                # Send 0 to ao1
                board.actuator.execute_task("ao1", 1, 0)
            elif (not can_actuate_ao1) and readings_ai1 >= MAX_READ_VALUE:
                # Can actuate back in ai1
                print "Can actuate back in ai1"
                can_actuate_ao1 = True

            # Reached the end of the loop without major problems
            board.sensor_down_count = 0
        except Exception, e:
            print "Board is not connected!\n" + str(e)

            # sensor_down_count will only be -1 when a failure occurs with no correct behaviour after
            if board.sensor_down_count != -1:
                board.sensor_down_count += 1
            if board.sensor_down_count == LIMIT_FAILS:
                utils.send_email("NI-USB Board", "The Board has been down for " + str(board.sensor_down_count) +
                                 " seconds!\nPlease check the connection as soon as possible")
                board.sensor_down_count = -1
                print "Sended email"
            print board.sensor_down_count
        time.sleep(TIMER_STEP)


class BoardInteraction(object):
    def __init__(self):
        """
        Class constrcutor
        """
        # Create the actuator and the reader with all the channels
        self.actuator = daqmxlib.Actuator(["ao0", "ao1"])
        self.reader = daqmxlib.Reader({"ai0": 1, "ai1": 1, "ai2": 1, "ai3": 1, "ai4": 1, "ai5": 1, "ai6": 1, "ai7": 1})
        self.sensor_down_count = 0

    def execute_task(self, name, num_samps_channel, message, auto_start=1, timeout=0):
        # Check if we can actuate in the given channel
        if name == "ao0" and not can_actuate_ao0:
            return False
        elif name == "ao1" and not can_actuate_ao1:
            return False
        print 'Executing task ' + str(name), message
        return self.actuator.execute_task(name, num_samps_channel, message, auto_start, timeout)

    def read_all(self, timeout=0.01, num_samples=None):
        return self.reader.read_all(timeout, num_samples)

    def change_collected_samples(self, physical_channel, number_samples):
        return self.reader.change_collected_samples(physical_channel, number_samples)


board_interaction = BoardInteraction()

# Make a Pyro4 daemon
daemon = Pyro4.Daemon(host='0.0.0.0', port=6000)
# Register the greeting object as a Pyro4 object
uri = daemon.register(board_interaction, '/NIBoard')

print "Going to create thread"

thread = threading.Thread(target=check_board, args=(board_interaction, ))
thread.start()

# Print the uri so we can use it in the client later
print "Ready. Object uri =", uri

# Start the event loop of the server to wait for calls
daemon.requestLoop()
