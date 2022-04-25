# Automatic Battery Cell AC Impedance Testing
#
# Equipment:
#   2x Keithley 2110 Bench Multimeter
#   1x Tektronix AFG1022 Arbitrary Function Generator

import os
from datetime import datetime
from time import sleep
import pyvisa

INFO_TEXT = \
"""AUTOMATIC BATTERY CELL AC IMPEDANCE TESTING
==========================================="""

AC_MEAS_AVERAGE_COUNT = 10
DC_MEAS_AVERAGE_COUNT = 5
TOTAL_CELLS = 630

def identifyInstruments(resourceManager):
    resources = resourceManager.list_resources()
    print("Detected instruments:")
    print(resources)
    print() # Empty line

    for index, instrumentStr in enumerate(resources):
        try:
            instrument = resourceManager.open_resource(instrumentStr)
            identity = instrument.query("*IDN?")
            print(f"{index + 1}. {instrumentStr}\n   {identity}")
            instrument.close()
        except: # TODO: Specify specific error type
            print((f"{index + 1}. {instrumentStr}\n   ERROR communicating with instrument"))

    return resources

def configureVoltmeterDC(voltDmm):
    voltDmm.write("CONFIGURE:VOLT:DC DEF,DEF") # Minimum range and resolution
    voltDmm.write("VOLTAGE:DC:RANGE:AUTO 1")
    voltDmm.write("AVERAGE:STATE ON")
    voltDmm.write("AVERAGE:TCONTROL REPEAT")
    voltDmm.write(f"AVERAGE:COUNT {DC_MEAS_AVERAGE_COUNT}")

def configureVoltmeterAC(voltDmm):
    voltDmm.write("CONFIGURE:VOLT:AC MIN,MIN") # Minimum range and resolution
    voltDmm.write("DETECTOR:BANDWIDTH 20")
    voltDmm.write("AVERAGE:STATE ON")
    voltDmm.write("AVERAGE:TCONTROL REPEAT")
    voltDmm.write(f"AVERAGE:COUNT {AC_MEAS_AVERAGE_COUNT}")

def configureAmmeterAC(currDmm):
    currDmm.write("CONFIGURE:CURR:AC MIN,MIN") # Minimum range and resolution
    currDmm.write("DETECTOR:BANDWIDTH 20")
    currDmm.write("AVERAGE:STATE ON")
    currDmm.write("AVERAGE:TCONTROL REPEAT")
    currDmm.write(f"AVERAGE:COUNT {AC_MEAS_AVERAGE_COUNT}")

def configureFuncGen(funcGen):
    funcGen.write("SOURCE1:FREQ:FIXED 1kHz")
    # Function generators can't source a lot of current and the impedances are very small,
    # so just set output to max
    funcGen.write("SOURCE1:VOLT:LEVEL:IMMEDIATE:AMPLITUDE MAX")
    funcGen.write("SOURCE1:VOLT:LEVEL:IMMEDIATE:OFFSET 0")

def getInputInt(prompt, limit):
    """Get an integer between 1 and limit, inclusive, from command line input with prompt"""
    while True: # Loop in case invalid input is received
        print(prompt, end = ": ")
        entry = input()
        try:
            entry = int(entry)
        except ValueError:
            entry = 0

        if entry not in range(1, limit + 1):
            print("Invalid selection.")
        else:
            break

    return entry

def getInputYesNo(prompt):
    print(f"{prompt} [y|n]: ", end = "")
    response = input()
    response = response.lower()
    while response not in ["y", "n"]:
        print("Invalid entry. Please try again. [y|n]: ", end = "")
        response = input()
        response = response.lower()
    return response

def getInputCellNumOrCancel(prompt):
    """Get an integer between 1 and limit, inclusive, or the letter c from command line input with prompt"""
    while True: # Loop in case invalid input is received
        print(prompt, end = ": ")
        entry = input()
        entry = entry.lower()
        if entry == "c":
            return "c"
        try:
            entry = int(entry)
        except ValueError:
            entry = 0

        if entry not in range(1, TOTAL_CELLS + 1) and entry != "c":
            print("Invalid selection.")
        else:
            break

    return entry

if __name__ == "__main__":
    print(INFO_TEXT)

    rm = pyvisa.ResourceManager()
    instruments = identifyInstruments(rm)
    numInstruments = len(instruments)

    if numInstruments == 0:
        print("ERROR: No instruments detected. Please correct the setup and run the program again.")
        exit(0)

    while True: # Loop in case instrument selection is incorrect
        index = getInputInt(f"Select the DMM measuring VOLTAGE [1-{numInstruments}]", numInstruments)
        print(f"Instrument {index} selected.")
        voltDmm = rm.open_resource(instruments[index - 1])

        index = getInputInt(f"Select the DMM measuring CURRENT [1-{numInstruments}]", numInstruments)
        print(f"Instrument {index} selected.")
        currDmm = rm.open_resource(instruments[index - 1])

        index = getInputInt(f"Select the FUNCTION GENERATOR [1-{numInstruments}]", numInstruments)
        print(f"Instrument {index} selected.")
        funcGen = rm.open_resource(instruments[index - 1])

        # Reset instruments to factory defaults for reliable starting point
        voltDmm.write("*RST")
        currDmm.write("*RST")
        funcGen.write("*RST")

        # Get user to verify setup
        voltDmm.write("DISPLAY:TEXT \"VOLTMETER\"")
        currDmm.write("DISPLAY:TEXT \"AMMETER\"")
        response = getInputYesNo((
            "Please look at the DMMs' displays and the VOLTMETER and AMMETER labels assigned. "
            "Do they match the setup wiring?"
        ))
        voltDmm.write("DISPLAY:TEXT:CLEAR")
        currDmm.write("DISPLAY:TEXT:CLEAR")
        if response == "y":
            break
        else:
            print("Please correct the instrument selection.")

    # Voltmeter is configured alternately between DC voltage and AC voltage. Configure for DC voltage for now
    configureVoltmeterDC(voltDmm)
    # Configure ammeter
    configureAmmeterAC(currDmm)
    # Configure function generator
    configureFuncGen(funcGen)

    # Open csv file in folder called "data" in same location as script to store measurements
    dateString = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
    filename = f"impedances {dateString}.csv"
    scriptPath = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(scriptPath, "data", filename)

    with open(filepath, mode="w") as file:
        file.write((
            "Cell Number,Timestamp,"
            "Open Circuit Voltage (V),AC Voltage (V),AC Current (A),AC Impedance (Ohms)\n"
        ))

        while True:            
            # Get a battery cell number. Test starts as soon as number is entered
            # Enter c and confirm to exit program
            cellNum = getInputCellNumOrCancel("Input cell number, or \"c\" to exit: ")
            if cellNum == "c":
                response = getInputYesNo("Are you sure you want to exit?")
                if response == "y":
                    break # End loop. File will be saved.
                else:
                    continue

            # Measure Open circuit voltage
            print("Measuring open circuit voltage...")
            configureVoltmeterDC(voltDmm)
            voltDmm.write("READ?")
            sleep(1)
            dcVoltage = float(voltDmm.read())

            # Check that voltage is within reason
            # If voltage is 0, likely that no cell is connected, go back to cell number entry
            # If voltage is outside reasonable range, that's bad so print a warning...
            if dcVoltage < 0.05:
                print("ERROR: Voltage is 0, is a battery cell inserted? Please try again.")
                continue # Don't save this measurement
            if dcVoltage < 2.7 or dcVoltage > 4.2:
                print("WARNING: Battery voltage reading outside expected range [2.7, 4.2] V")

            print(f"Open Circuit Voltage: {dcVoltage:.6f} V")

            print("Measuring impedance...")
            configureVoltmeterAC(voltDmm)

            # Enable func gen, give it a moment to power up
            funcGen.write("OUTPUT1:STATE ON")

            # Measure voltage and current, record current time
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            voltDmm.write("READ?")
            currDmm.write("READ?")
            sleep(AC_MEAS_AVERAGE_COUNT) # 1s per measurement
            acVoltage = float(voltDmm.read())
            acCurrent = float(currDmm.read())

            # Disable func gen
            funcGen.write("OUTPUT1:STATE OFF")

            # Check that current is reasonable
            # If current is 0, likely that something was disonnected...
            # go back to cell number entry
            if acCurrent < 0.05:
                print("ERROR: Current is 0, is something disconnected? Please try again.")
                continue # Don't save measurements

            # If measurement is reasonable, display it with computed impedance
            impedance = acVoltage / acCurrent

            print(f"Voltage:   {acVoltage * 1000.0:.6f} mV AC")
            print(f"Current:   {acCurrent * 1000.0:.2f} mA AC")
            print(f"Impedance: {impedance:.6f} Ohms")

            # Save measurements to CSV with timestamp
            file.write(f"{cellNum},{timestamp},{dcVoltage},{acVoltage},{acCurrent},{impedance}\n")

    # Exit from remote mode on DMMs to re-enable front panel for convenience
    voltDmm.write("SYSTEM:LOCAL")
    currDmm.write("SYSTEM:LOCAL")

    voltDmm.close()
    currDmm.close()
    funcGen.close()
