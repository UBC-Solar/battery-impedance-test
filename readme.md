# Battery Cell Impedance Measurement

This is a python script for interfacing with several pieces of bench equipment in order to make AC impedance measurements of battery cells.

## Equipment and Physical Setup

1. Have all of the following:
    - 2x Keithley 2110 Bench Multimeter
    - 1x Tektronix AFG1022 Arbitrary Function Generator
    - 1x 100uF 16V (electrolytic) capacitor
    - 1x Function generator cable
    - 4x Alligator clip to banana plug cables
    - Batteries to be tested
2. (Optional) Attach metal tabs to batteries-in-test. This step can be done to get better readings for 18650 and 21700 batteries, but is redundant for pouch cells. **Note attaching tabs is irreversible.**
    1. Prepare spot welder
    2. Prepare two 1" long, thin nickel strips per cell
    3. Spot weld one nickel strip onto each end of the cell. [Here's a guide](https://wiki.ubcsolar.com/en/subteams/battery/docs/Battery-Manufacturing#spot-welding).

<p align="center">
  <img src="https://raw.githubusercontent.com/a2k-hanlon/auto-impedance-test/main/images/setupDiagram.drawio.svg">
</p>

> Circuit diagram. "Battery" is the battery being tested. Lines with arrows are USB cables.

<p align="center">
  <img width=450px src="https://raw.githubusercontent.com/a2k-hanlon/auto-impedance-test/main/images/setup.jpg">
</p>

## Program Setup

### We're going to need the following dependencies:

- A VISA implementation on the host computer. NI-VISA is a popular one. Download it from https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html .
  - For Linux/Mac: note that only the runtime is strictly required for this program, but you can install the full suite if you wish
- PyVISA library, for interfacing with VISA-enabled instruments from Python
  
### First time setup to run the program is as follows:

1. Install Python (recommended version is 3+) if you haven't already. Ideal method is through https://www.python.org/downloads/ . However, programming softwares like PyCharm can also run this script.
2. Install a VISA Implementation such as NI-VISA
3. Open PowerShell / Command Prompt / Terminal / PyCharm. For PyCharm, open the command line in PyCharm.
4. Create a python virtual environment
```shell
python -m venv venv
```
5. Install python dependencies
```shell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Testing Procedure

1. Open PowerShell / Command Prompt / Terminal / PyCharm. For PyCharm, open the command line in PyCharm.
2. Activate virtual environment
```shell
. venv/bin/activate # Linux / Mac
venv/Scripts/activate # Windows
```
3. Make sure instruments are connected
4. Run the script
```shell
python main.py
```
5. Follow the instructions given by the program to identify the instruments, confirm the instrument identification and run the test. Note: the script will give you a bunch of serial numbers to identify instruments. Look on the back of your instruments for their serial numbers.


The script will save all of the measurements to a new file in the `data` folder called `impedances <timestamp>.csv`.

Any time the program prints an ERROR during the measurement routine, it will not save the measurement. If this occurs, make sure the problem is corrected and re-run the test on the battery cell. If a WARNING is printed, it will still save a measurement.

Don't worry about measuring the same cell twice. The program will never overwrite existing data, and a timestamp is saved with each entry of data from a run of the test.
