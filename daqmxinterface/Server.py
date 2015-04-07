# coding: utf-8
__author__ = 'Joaquim Leitão'

# Imports to be used in the code
import time
import threading
import daqmxlib
import Pyro4

# Global Variables definition
global MIN_READ_VALUE
global MAX_READ_VALUE
global can_actuate_ao0
global can_actuate_ao1
global board_connected

MIN_READ_VALUE = -6
MAX_READ_VALUE = -5
can_actuate_ao0 = True
can_actuate_ao1 = True
board_connected = True

# Constants definition
TIMER_STEP = 1.0


def check_board(board):
    """
    Method that monitors the activity of the NI Board, checking for connection problems and for the liquid level in the
    two main containers. Whenever the volume of liquid exceeds the limit then the user actuation stops until it reaches
    a safe level, at which point the user actuation is enabled again
    :param board: The class that implements the necessary methods to remotely interact with the NI Board
    """
    global MIN_READ_VALUE
    global can_actuate_ao0
    global can_actuate_ao1
    global board_connected

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
            board_connected = True
        except Exception, e:
            print "Board is not connected!\n" + str(e)
            board_connected = False
        time.sleep(TIMER_STEP)


class BoardInteraction(object):
    """
    Class that implements the necessary methods to remotely interact with the NI Board (Via Python Pyro4), making use of
    the PyDAQmx and the daqmxlib Python libraries. In this class we can find two main methods:
    A method that allows the user to actuate in a given physical channel and a method to read the contents in all the
    available physical channels. There is also a method to change the number of samples to collect in a given physical
    channel.
    """
    def __init__(self):
        """
        Class constructor
        """
        # Create the actuator and the reader with all the channels
        self.actuator = daqmxlib.Actuator(["ao0", "ao1"])
        self.reader = daqmxlib.Reader({"ai0": 1, "ai1": 1, "ai2": 1, "ai3": 1, "ai4": 1, "ai5": 1, "ai6": 1, "ai7": 1})

    def execute_task(self, name, num_samps_channel, message, auto_start=1, timeout=0):
        """
        Executes a given task, starting its actuation (That is, sends a given message to a given actuator)
        :param name: The name of the task to execute
        :param num_samps_channel: The number of samples, per channel, to write
        :param message: The message to send to the actuator
        :param auto_start: Specifies whether or not this function automatically starts the task if you do not start it.
        :param timeout: The amount of time, in seconds, to wait for this function to write all the samples
                        (-1 for inifinite)
        :return: A boolean value, indicating the success or failure of the execution. This method may also return None
                 if the NI Board is not connected
        """

        global board_connected

        if not board_connected:
            return None
            
        # Check if we can actuate in the given channel
        if name == "ao0" and not can_actuate_ao0:
            return False
        elif name == "ao1" and not can_actuate_ao1:
            return False
        print 'Executing task ' + str(name), message
        return self.actuator.execute_task(name, num_samps_channel, message, auto_start, timeout)

    def read_all(self, timeout=0.01, num_samples=None):
        """
        Reads data from all the active physical channels
        :param timeout: The amount of time, in seconds, to wait for the function to read the sample(s)
                        (-1 for infinite)
        :param num_samples: A list with the number of samples to acquire for each channel
        :return: Returns a dictionary with the data read from all the active physical channels. This method may also
                 return None if the NI Board is not connected
        """

        global board_connected

        if not board_connected:
            return None
        return self.reader.read_all(timeout, num_samples)

    def change_collected_samples(self, physical_channel, number_samples):
        """
        Changes the number of samples collected in the specified physical channel
        :param physical_channel: The desired physical channel
        :param number_samples: The new number of samples to collect. This method may also return None if the NI Board
                               is not connected
        """

        global board_connected

        if not board_connected:
            return None
        return self.reader.change_collected_samples(physical_channel, number_samples)


# Create a Board Interaction object
board_interaction = BoardInteraction()

# Make a Pyro4 daemon
daemon = Pyro4.Daemon(host='0.0.0.0', port=6000)
# Register the greeting object as a Pyro4 object
uri = daemon.register(board_interaction, '/NIBoard')

# Set up a thread to monitor the board
thread = threading.Thread(target=check_board, args=(board_interaction, ))
thread.start()

# Print the uri so we can use it in the client later
print "Ready. Object uri =", uri

# Start the event loop of the server to wait for calls
daemon.requestLoop()
