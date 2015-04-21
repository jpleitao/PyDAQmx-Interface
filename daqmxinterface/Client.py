# coding: utf-8
__author__ = 'Joaquim Leitão'

# Imports to be used in the code
import Pyro4.core
import math
import time

# Pyro4 Specific data
port = 6000
name = "NIBoard"
uri = "PYRO:/" + name + "@localhost:" + str(port)

# Get a Pyro4 proxy to the greeting object
board_interaction = Pyro4.Proxy(uri)

while True:
    valor = raw_input("Insere o valor")
    board_interaction.execute_task("ao0", 1, float(valor))

"""
# Generate the actuation signal
x = [i for i in range(10)]
data = [abs(math.sin(i)) for i in x]
print data

# Send each value to the board, specifying the desired physical channel where the actuation is going to be performed
# (in this case the actuation is going to take place in the physical channel ao0)
for current in data:
    result = board_interaction.execute_task("ao0", 1, current)
    print "Executing task... " + str(result) + "!"
    time.sleep(1)

# Read all the channels with previously defined number of samples
print board_interaction.read_all()

# Read all the channels with a specified number of samples per channel
print board_interaction.read_all(num_samples={"ai0": 3, "ai1": 3, "ai2": 3, "ai3": 3, "ai4": 3, "ai5": 3,
                                              "ai6": 3, "ai7": 3})
"""