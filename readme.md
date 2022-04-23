# Battery Cell Impedance Measurement Utility

This is a python script for interfacing with several pieces of bench equipment in order to make AC impedance measurements of battery cells.

## Equipment

- 2x Keithley 2110 Bench Multimeter
- 1x Tektronix AFG1022 Arbitrary Function Generator

## Dependencies

- A VISA implementation on the host computer. NI-VISA is a popular one. Download it from https://www.ni.com/en-ca/support/downloads/drivers/download.ni-visa.html#442805.
    - Note that only the runtime is strictly required for this program, but you can install the full suite if you wish
- PyVISA library, for interfacing with VISA-enabled instruments from Python

## Program Setup

First time setup to run the program is as follows:

1. Install a VISA Implementation such as NI-VISA
2. Create a python virtual environment

```shell
$ python -m venv venv
```

2. Install python dependencies

```shell
$ python -m pip install --upgrade pip
$ python -m pip install -r requirements.txt
```