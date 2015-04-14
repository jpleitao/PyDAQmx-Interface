# PyDAQmx-Interface
Interface for the National Instruments boards NI USB 6008 and NI USB 6009 using the official driver and the PyDAQmx python 2.7 implementation


## Requirements
In order to successfully run the contents of this package the following requirements must be met:

* Python 2.7
* NIDAQmx driver (only tested on the windows version)
* PyDAQmx package (available in the PyDAQmx-1.3.1 directory of this repository or at http://pythonhosted.org/PyDAQmx/ or at the package's official github repository page https://github.com/clade/PyDAQmx)

## Installation 
### PyDAQmx ([source](http://pythonhosted.org/PyDAQmx/))

Manual mode:

1. Download the [PyDAQmx package](https://pypi.python.org/packages/source/P/PyDAQmx/PyDAQmx-1.3.1.tar.gz)
2. Unpack it 
3. ```  python setup.py install```

Or via pip:

1. ```  pip install PyDAQmx```

The package is written for Python 2. Is is compatible with Python 3 using 2to3. To build and install the package with Python 3

     python setup.py build
     python setup.py install


If you want to run PyDAQmx without installing it, run the python setup.py build command and switch to the build/lib directory.

### Windows - NIDAQmx driver
1. Download and install the [NIDAQmx driver](http://ftp.ni.com/support/softlib/multifunction_daq/nidaqmx/9.8/NIDAQ980f3_downloader.exe)


### Linux 

* Not supported yet

## Usage

### Direct Interaction with DAQmxLib
A reader and actuator examples are presented in the ```  daqmxinterface ```  directory of this repository. Please see ```  daqmxinterface/actuator_example.py ``` and  ```  daqmxinterface/reader_example.py ``` 

### Remote Method Invocation with Pyro4
A Pyro4 client application example is presented in the ```  daqmxinterface ```  directory of this repository. Please see ```  daqmxinterface/Client.py ```   