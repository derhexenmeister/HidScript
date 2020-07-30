################################################################################
# Simple CircuitPython example of a HidScript Interpreter
#
# Installation:
# Copy hidscript.py or hidscript.mpy into the CIRCUITPY/lib directory
#
# Basic Usage:
#     from hidscript import HidScript
#     hid = HidScript()
#     hid.process("rickroll.txt")
#
# More advanced usage is board specific. You could use buttons to trigger the
# execution of specific scripts.
#
# NOTES:
#     The CIRCUITPY drive is available for use as mass storage by the host OS. The
#     amount of free space depends upon the platform used.
#
#     On a constrained system such as the Seeeduino Xiao only install the required
#     libraries:
#
#     adafruit_hid/
#         __init__.mpy
#         keyboard_layout_us.mpy
#         keyboard.mpy
#         keycode.mpy
#
# TODO:
#     Minimize RAM usage to allow for more features
#
#     Support key combinations of 3 or more keys specified as arguments?
#     For now we use the argument with tuples such as CTRL-SHIFT, so it's not urgent.
#     Look at https://github.com/hak5/bashbunny-payloads/blob/master/languages/us.json
#
#     Support scripting the mouse? 
#     Alternative - https://www.computerhope.com/issues/ch000542.htm
#
#     Support scripting the virtual serial connection?
#     Look into extensions such as a multi-command REPEAT?
#     Support scripting the keyboard language? Maybe fine to just do via CircuitPython script
#     Support scripting the on-board LED? See https://docs.hak5.org/hc/en-us/articles/360010554513-LED
#     Support a button press in the script? See https://docs.hak5.org/hc/en-us/articles/360010554673-BUTTON
#
#     Is the default USB Vendor ID ok? Doesn't cause Macs to ask about profiling the keyboard?
#     (May be board dependent)
#
# License:
#     Note that this processes a script format which is similar to Ducky Script.
#     Ducky Script is copyrighted by and a trademark of Hak5 LLC.
#     See https://docs.hak5.org/hc/en-us/articles/360049449314-Ducky-Script-Command-Reference
#
#     Do not use this in a way which would conflict with Hak5's copyright, and
#     take a look at their website for other interesting products.
#
#     Other than the above advice, this CircuitPython file is licensed as follows:
# 
#     Copyright © 2020 Keith Evans
#
#     This work is free. You can redistribute it and/or modify it under the
#     terms of the Do What The Fuck You Want To Public License, Version 2,
#     as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.
#
################################################################################
import time
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
#from adafruit_hid.mouse import Mouse
import usb_hid

class HidScript:
    def __init__(self, debug=False):
        self.debug = debug
        #self.mouse = Mouse(usb_hid.devices)
        self.keyboard = Keyboard(usb_hid.devices)
        self.keyboard_layout = KeyboardLayoutUS(self.keyboard)  # Change for non-US
        self.default_delay = 0
        self.string_delay = 0
        self.last_cmd = ""
        self.last_arg = ""

        # Keycode only has US mappings, not sure if AdaFruit has others
        #
        # TODO - consider a data structure which consumes less RAM for
        # constrained platforms.
        #
        # Keep a separate structure for multi-key combos to lower memory
        # usage.
        #
        self.tuple_keymap = {
            "CTRL-ALT": (Keycode.CONTROL, Keycode.ALT),
            "CTRL-SHIFT": (Keycode.CONTROL, Keycode.SHIFT),
            "ALT-SHIFT": (Keycode.ALT, Keycode.SHIFT)
        }

        self.keymap = {
            "ALT": Keycode.ALT,
            "APP": Keycode.APPLICATION,
            "BREAK": Keycode.PAUSE,
            "CAPSLOCK": Keycode.CAPS_LOCK,
            "CONTROL": Keycode.CONTROL,
            "CTRL": Keycode.CONTROL,
            "DELETE": Keycode.DELETE,
            "DOWNARROW": Keycode.DOWN_ARROW, "DOWN": Keycode.DOWN_ARROW,
            "END": Keycode.END,
            "ENTER": Keycode.ENTER,
            "ESC": Keycode.ESCAPE, "ESCAPE": Keycode.ESCAPE,
            "GUI": Keycode.GUI,
            "HOME": Keycode.HOME,
            "INSERT": Keycode.INSERT,
            "LEFTARROW": Keycode.LEFT_ARROW, "LEFT": Keycode.LEFT_ARROW,
            "MENU": Keycode.APPLICATION,
            "NUMLOCK": Keycode.KEYPAD_NUMLOCK,
            "PAGEUP": Keycode.PAGE_UP, "PAGEDOWN": Keycode.PAGE_DOWN,
            "PAUSE": Keycode.PAUSE,
            "PRINTSCREEN": Keycode.PRINT_SCREEN,
            "RIGHTARROW": Keycode.RIGHT_ARROW, "RIGHT": Keycode.RIGHT_ARROW,
            "SCROLLLOCK": Keycode.SCROLL_LOCK,
            "SHIFT": Keycode.SHIFT,
            "SPACE": Keycode.SPACE,
            "TAB": Keycode.TAB,
            "UPARROW": Keycode.UP_ARROW, "UP": Keycode.UP_ARROW,
            "WINDOWS": Keycode.WINDOWS,
            "a": Keycode.A, "A": Keycode.A,
            "b": Keycode.B, "B": Keycode.B,
            "c": Keycode.C, "C": Keycode.C,
            "d": Keycode.D, "D": Keycode.D,
            "e": Keycode.E, "E": Keycode.E,
            "f": Keycode.F, "F": Keycode.F,
            "g": Keycode.G, "G": Keycode.G,
            "h": Keycode.H, "H": Keycode.H,
            "i": Keycode.I, "I": Keycode.I,
            "j": Keycode.J, "J": Keycode.J,
            "k": Keycode.K, "K": Keycode.K,
            "l": Keycode.L, "L": Keycode.L,
            "m": Keycode.M, "M": Keycode.M,
            "n": Keycode.N, "N": Keycode.N,
            "o": Keycode.O, "O": Keycode.O,
            "p": Keycode.P, "P": Keycode.P,
            "q": Keycode.Q, "Q": Keycode.Q,
            "r": Keycode.R, "R": Keycode.R,
            "s": Keycode.S, "S": Keycode.S,
            "t": Keycode.T, "T": Keycode.T,
            "u": Keycode.U, "U": Keycode.U,
            "v": Keycode.V, "V": Keycode.V,
            "w": Keycode.W, "W": Keycode.W,
            "x": Keycode.X, "X": Keycode.X,
            "y": Keycode.Y, "Y": Keycode.Y,
            "z": Keycode.Z, "Z": Keycode.Z,
            #
            # The DuckyScript encoder didn't appear to have the following codes and
            # probably used the STRING command to deal with some of them. Adding them shouldn't
            # hurt but does consume RAM. Some are Mac specific.
            #
            "0": Keycode.ZERO,  "1": Keycode.ONE,
            "2": Keycode.TWO,   "3": Keycode.THREE,
            "4": Keycode.FOUR,  "5": Keycode.FIVE,
            "6": Keycode.SIX,   "7": Keycode.SEVEN,
            "8": Keycode.EIGHT, "9": Keycode.NINE,
            "F1": Keycode.F1,   "F2": Keycode.F2,
            "F3": Keycode.F3,   "F4": Keycode.F4,
            "F5": Keycode.F5,   "F6": Keycode.F6,
            "F7": Keycode.F7,   "F8": Keycode.F8,
            "F9": Keycode.F9,   "F10": Keycode.F10,
            "F11": Keycode.F11, "F12": Keycode.F12,
            "F13": Keycode.F13, "F14": Keycode.F14,
            "F15": Keycode.F15, "F16": Keycode.F16,
            "F17": Keycode.F17, "F18": Keycode.F18,
            "F19": Keycode.F19,
            "BACKSLASH": Keycode.BACKSLASH,
            "COMMA": Keycode.COMMA,
            "COMMAND": Keycode.COMMAND,
            "FORWARD_SLASH": Keycode.FORWARD_SLASH,
            "GRAVE_ACCENT": Keycode.GRAVE_ACCENT,
            "LEFT_BRACKET":  Keycode.LEFT_BRACKET,
            "OPTION": Keycode.ALT,
            "PERIOD": Keycode.PERIOD,
            "POUND": Keycode.POUND,
            "QUOTE": Keycode.QUOTE,
            "RIGHT_ALT": Keycode.RIGHT_ALT,
            "RIGHT_BRACKET": Keycode.RIGHT_BRACKET,
            "RIGHT_CONTROL": Keycode.RIGHT_CONTROL,
            "RIGHT_GUI": Keycode.RIGHT_GUI,
            "RIGHT_SHIFT": Keycode.RIGHT_SHIFT,
            "SEMICOLON": Keycode.SEMICOLON
        }

    # Execute a single command in a HidScript file
    # REPEAT handled in process
    #
    def _exec_cmd(self, cmd, arg):
        if cmd == "REM":
            if self.debug: print("Comment: REM ", arg)
        elif cmd == "STRING":
            if self.debug: print("String: STRING ", arg)
            if self.string_delay:
                for c in arg:
                    self.keyboard_layout.write(c)
                    time.sleep(self.string_delay)
            else:
                self.keyboard_layout.write(arg)
        elif cmd in self.keymap:
            if arg and arg in self.keymap:
                self.keyboard.send(self.keymap[cmd], self.keymap[arg])
            else:
                self.keyboard.send(self.keymap[cmd])
        elif cmd in self.tuple_keymap:
            for keycode in self.tuple_keymap[cmd]:
                self.keyboard.press(keycode)
            if arg and arg in self.keymap:
                self.keyboard.send(self.keymap[arg])
            else:
                self.keyboard.release_all()

        if cmd == "DELAY":
            if self.debug: print("Delay: DELAY ", arg)
            time.sleep(int(arg)/100.0)
        elif (cmd == "DEFAULTDELAY") or (cmd == "DEFAULT_DELAY"):
            if self.debug: print("Default delay: DEFAULTDELAY ", arg)
            self.default_delay = int(arg)/100.0
        elif (cmd == "STRINGDELAY") or (cmd == "STRING_DELAY"):
            if self.debug: print("String delay: STRING_DELAY ", arg)
            self.string_delay = int(arg)/1000.0
        else:
            time.sleep(self.default_delay)

    # Process a HidScript file
    #
    def process(self, scriptname):
        try:
            with open(scriptname) as f:
                for line in f: 
                    # Eliminate leading or trailing whitespace
                    # TODO - does this break any STRING commands?
                    #
                    line = line.strip()
                    values = line.split(" ", 1)
                    if self.debug: print("Script line: ", values[0])
                    cmd = values[0]
                    if len(values) == 2:
                        arg = values[1]
                    else:
                        arg = ""

                    # Handle REPEAT command at this level, but all other commands
                    # are handled by _exec_cmd()
                    #
                    if cmd == "REPEAT":
                        arg = int(arg)
                        for i in range(arg):
                            self._exec_cmd(self.last_cmd, self.last_arg)
                    else:
                        self.last_cmd = cmd
                        self.last_arg = arg
                        self._exec_cmd(cmd, arg)

        except OSError:
            if self.debug: print("Could not read file: ", scriptname)

