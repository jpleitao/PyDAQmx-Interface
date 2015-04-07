# coding: utf-8
__author__ = 'Joaquim Leitão'

import time
import traceback
import sys
import threading

import daqmxlib
import Pyro4

TIMER_STEP = 1.0


def check_board(board):
    while True:
        try:
            # print "Going to read"
            board.read_all()
            # print "Done!"
        except Exception, e:
            print "Board is not connected!"
        time.sleep(TIMER_STEP)


class BoardInteraction(object):
    def __init__(self):
        """
        Class constrcutor
        """
        # Create the actuator and the reader with all the channels
        self.actuator = daqmxlib.Actuator(["ao0", "ao1"])
        self.reader = daqmxlib.Reader({"ai0": 1, "ai1": 1, "ai2": 1, "ai3": 1, "ai4": 1, "ai5": 1, "ai6": 1, "ai7": 1})

    def execute_task(self, name, num_samps_channel, message, auto_start=1, timeout=0):
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
