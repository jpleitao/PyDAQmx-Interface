# PyDAQmx-Interface
Interface for the National Instruments boards NI USB 6008 and NI USB 6009 using the official driver and the PyDAQmx python 2.7 implementation


## Requirements
In order to successfully run the contents of this package the following requirements must be met:

* Python 2.7
* NIDAQmx driver (only tested on the windows version)
* PyDAQmx package (available in the PyDAQmx-1.3.1 directory of this repository or at http://pythonhosted.org/PyDAQmx/)

## Installation 
### Windows - PyDAQmx

Manual mode:

1. Download the [PyDAQmx package](https://pypi.python.org/packages/source/P/PyDAQmx/PyDAQmx-1.3.1.tar.gz)
2. Unpack it 
3. ```python setup.py install```

Or via pip:

1. ```pip install PyDAQmx```
  
### Windows - NIDAQmx driver
1. Download and install the [NIDAQmx driver](http://ftp.ni.com/support/softlib/multifunction_daq/nidaqmx/9.8/NIDAQ980f3_downloader.exe)


### Linux 

* Not supported yet