# Example code for Seeeduino Xiao
# Ground pin D1 (opposite GND pin) to prevent HID script from running
#
from hidscript import HidScript
from digitalio import DigitalInOut, Direction, Pull
import board

switch = DigitalInOut(board.D1)
switch.direction = Direction.INPUT
switch.pull = Pull.UP

serialDebug=True
scriptName="rickroll.txt"

if switch.value:
    if serialDebug:
        print("Running HidScript: ", scriptName)
    hid = HidScript(serialDebug)
    hid.process(scriptName)
elif serialDebug:
    print("Skipping HidScript")