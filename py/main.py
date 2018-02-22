#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Joshua Neighbarger
# Version: 22 February 2018
# Email: jneigh@uw.edu

"""DynamicShell

This module implements a dynamically defined shell which allows for the import/reimport of named modules. The intent is
to create the module as abstractly as possible to allow simple configuration and adaptation to a wide range of future
projects. Commands (attributes), metadata, formatting, etc are defined globally upon import of this module. For a short
description of each attribute, reference the COMMANDS global variable in this module.

Attributes:
    TEXT_FORMAT (dict): Maps user-defined stdout cases (i.e.: log, input, etc.) to a string which will change the
        console text format and colors when printed.
    MODULE_PKG (str): The name of the folder in which all modules are loaded from.
    COMMANDS (dict): Maps all typed commands recognized by the shell to a tuple, which contains a Python-equivalent to
        the function pointer, the number of arguments required by the call, and a short description of each command to
        be printed in the help message. If the number of arguments is (-1), the call accepts all arguments such that
        0 <= argv < infinity, where argv is the number of arguments passed. Individual commands may further require a
        minimum number of arguments and should check for argument validity.
    METADATA (dict): Contains various data, including the application name, the authors of the project, the version of
        the application, etc. This attribute is included because this module is intended to be used as a driver for
        another application or module.
    HEADER (str): Printed upon start of this module. Contains the name of the application and version, as defined in
        METADATA.
    PROMPT (str): The string to be printed with each call to input(str).
    MODULES (dict): Maps all loaded module names to the respective module reference. This simplifies the process of
        reloading modules and eliminates the need to interact with sys.modules and crying over how poorly documented
        importlib (if you're reading this and know a better way, please email me).
    LOG_LEVEL (int): The level of logs which are to be displayed. See the log method in this module.
    COLORS_ENABLED (bool): If the console log colors are to be enabled or disabled.

Todo:
    * Separate launched module to separate process and console to allow for use of both modules synchronously.
    * Clean up argument parameters between functions to properly implement optional parameters.

"""

import importlib
import os


def launch_module(*args: tuple):
    """Dynamically launches a named module.

    Passed arguments are optional, and will be prompted if not defined. Modules
    are loaded on their first call and are reloaded after each subsequent call to allow for the module to be edited
    or created and then launched with this attribute without needing to restart the module. All modules will implement
    the launch method to utilize this functionality.

    Args:
        *args: The arguments passed to this function.

    Returns:
        None
    """
    if not args:
        args = input("What to launch? ").strip().split()
    else:
        args = args[0]

    module = import_module(args[0])
    if module:
        if len(args) == 1:
            module.launch()
        else:
            module.launch(args)
    else:
        print("Module \"", args[0], "\" not launched", sep="")


def test_module(*args: tuple):
    """Dynamically tests a named module.

    Passed arguments are optional, and will be prompted if not defined. Modules
    are loaded on their first call and are reloaded after each subsequent call to allow for the module to be edited
    or created and then tested with this attribute without needing to restart the module. All modules will implement
    the launch method to utilize this functionality. Modules which implement the test function return a boolean True or
    False, indicating if that module passed all of its tests.

    Args:
        *args: The arguments passed to this function.

    Returns:
        If the specified module passed all of its tests.
    """
    if not args:
        args = input("What to test? ").strip().split()
    else:
        args = args[0]

    module = import_module(args[0])
    if module:
        if len(args) == 1:
            return module.test()
        else:
            return module.test(args)
    else:
        print("Module \"", args[0], "\" not tested", sep="")


def import_module(filename):
    """ Imports the specified module.

    Imported modules are added to the MODULES attribute, and its commands, if any, are added to the COMMANDS attribute.

    Args:
        filename: The file in which the module is contained.

    Returns:
        The newly imported or reimported module.
    """
    global COMMANDS
    global MODULES
    try:
        if type(filename) is list:
            filename = filename[0]
        if filename in MODULES:
            module = importlib.reload(MODULES[filename])
        else:
            module = importlib.import_module("." + filename, MODULE_PKG)
            MODULES[filename] = module
        try:
            COMMANDS = dict(COMMANDS, **module.get_commands())
        except AttributeError:
            log(1, "\"", filename, "\" module has no defined attribute \'get_commands\'", sep='')
        except TypeError:
            log(0, "\"", filename, "\" module's command definition is not in the proper format", sep='')
        return module
    except ModuleNotFoundError:
        log(0, "No such module (\"", filename, "\")", sep="")
        return None


def import_all_commands():
    """ Imports all modules within MODULE_PKG.

    Returns:
        None
    """
    attempted = 0
    succeeded = 0
    log(2, "Loading modules...")
    for filename in os.listdir(MODULE_PKG):
        if filename.endswith(".py"):
            attempted += 1
            filename = filename[:-3]
            if import_module(filename):
                succeeded += 1
    log(2, "Successfully loaded", succeeded, "of", attempted, "modules")


def echo(var: str):
    var = var[0].lower()
    if var == "commands":
        log(2, *[cmd for cmd in COMMANDS], sep='\n\t')
    elif var == "modules":
        log(2, *[mod for mod in MODULES], sep='\n\t')
    else:
        log(0, "Variable not registered or found")


def show_help():
    """Shows the help text to the console.

    Prints the name, number of arguments, and description of each command in a user-friendly manner to the Python
    console. Commands which require -1 arguments will accept all passed arguments delimited by a ' ' character.

    Returns:
        None
    """
    for cmd in COMMANDS:
        print(cmd, " (", COMMANDS[cmd][1], " args):\t\t", COMMANDS[cmd][2], sep="")


def info():
    """Prints the metadata in a user-friendly manner to the Python console.

    Returns:
        None
    """
    for key in METADATA:
        print(key, ":  \t", sep="", end="")
        for value in METADATA[key]:
            print(value, end=",  ")
        print()


def log(level: int, *args, **kwargs):
    """Logs the message to console.

    Writes the passed message to the console at the defined log level. Each log level is tagged with their name and is
    color-coded for the standard terminal. Multi-color support can be disabled globally, as well as the filtered log
    level. The global log level, LOG_LEVEL, must be greater than the local level. For example, all logs are disabled if
    the global log level is 0. Log levels are defined as follows:
        {
            ERROR: 0,
            WARNING: 1,
            DEBUG: 2
        }

    Args:
        level: The level of log message
        args: The message to be written
        kwargs: The additional keyword-based args for the print statement

    Returns:
        None
    """
    kwargs["flush"] = True
    if level is 0 and LOG_LEVEL > 0:
        print((TEXT_FORMAT["error"] if COLORS_ENABLED else "") + "ERR:  ", *args,
              (TEXT_FORMAT["default"] if COLORS_ENABLED else ""), **kwargs)
    elif level is 1 and LOG_LEVEL > 1:
        print((TEXT_FORMAT["warning"] if COLORS_ENABLED else "") + "WARNING:  ", *args,
              (TEXT_FORMAT["default"] if COLORS_ENABLED else ""),  **kwargs)
    elif level is 2 and LOG_LEVEL > 2:
        print((TEXT_FORMAT["debug"] if COLORS_ENABLED else "") + "DEBUG:  ", *args,
              (TEXT_FORMAT["default"] if COLORS_ENABLED else ""), **kwargs)
    else:
        print(" ".join(map(str, args)))


def main():
    """The main method.

    Handles the main loop and executes commands by name as passed through the command line.

    Returns:
        None
    """
    print((TEXT_FORMAT["default"] if COLORS_ENABLED else "") + HEADER)
    import_all_commands()
    while 1:
        i = input(PROMPT).strip().split()
        if not i:
            continue
        elif not COMMANDS.get(i[0]):
            log(2, "Command \"", i[0], "\" does not exist or is misspelled", sep='')
        elif (COMMANDS.get(i[0])[1] != len(i) - 1) and (COMMANDS.get(i[0])[1] != -1):
            log(2, "Invalid number of args for command ", i[0],
                "(defined: ", COMMANDS.get(i[0])[1], ", passed: ", len(i) - 1, ")", sep="")
        elif len(i) == 1:
            COMMANDS[i[0]][0]()
        else:
            COMMANDS[i[0]][0](i[1:])


# Color     Text    BG  |   Style
# Black     30      40  |   No Effect   0
# Red       31      41  |   Bold        1
# Green     32      42  |   Underline   2
# Yellow    33      43  |   Negative1   3
# Blue      34      44  |   Negative2   4
# Purple    35      45  |
# Cyan      36      46  |
# White     37      47  |
TEXT_FORMAT = {
    "default": "\033[0;37;40m",
    "warning": "\033[0;33;40m",
    "debug": "\033[0;36;40m",
    "error": "\033[0;31;40m"
}
MODULE_PKG = "modules"
COMMANDS = {
        "quit": (quit, 0, "Exit the program"),
        "q": (quit, 0, "Exit the program"),
        "help": (show_help, 0, "Outputs each command and their description"),
        "about": (info, 0, "Outputs the metadata of the application"),
        "info": (info, 0, "Outputs the metadata of the application"),
        "launch": (launch_module, -1, "Launches the specified module with the defined args"),
        "test": (test_module, -1, "Tests the specified module with the defined args"),
        "import_all": (import_all_commands, 0, "Loads all commands from modules"),
        "import": (import_module, 1, "Loads a specified module"),
        "echo": (echo, 1, "Echos passed variable to the console")
    }
METADATA = {
    "Authors": ("Joshua Neighbarger", "Karan Singla", "Zachary Chandler"),
    "App Name": ("NLP Chat Console (Alan)",),
    "Version": ("21 February 2018",)
}
HEADER = METADATA["App Name"][0] + ",  " + METADATA["Version"][0]
PROMPT = ">>>:  "
MODULES = {}
LOG_LEVEL = 4
COLORS_ENABLED = True

if __name__ == "__main__":
    main()
