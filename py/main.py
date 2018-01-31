#!/usr/bin/python
# Author: Joshua Neighbarger
# Version: 30 January 2018
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

Todo:
    * Add returns definitions to docstrings
    * Consider exporting the COMMAND definitions to an external Python module to allow for dynamically defined modules.
        Methods may be referenced to the imported module and said module may be handled as a plugin.
    * Consider defining an auto-import feature which will either automatically import all modules from the modules
        folder or import all modules from a defined external file (likely the former rather than the latter).
    * Add escape tokens to prompts and messages to allow the console to be styled, as described in TEXT_FORMAT.

"""

import importlib


def launch(*args: tuple):
    """Dynamically launches a named module.

    Passed arguments are optional, and will be prompted if not defined. Modules
    are loaded on their first call and are reloaded after each subsequent call to allow for the module to be edited
    or created and then launched with this attribute without needing to restart the module.

    Args:
        *args: The arguments passed to this function.

    Returns:
        None
    """
    try:

        if not args:
            args = input("What to launch? ").strip().split()
        else:
            args = args[0]

        if args[0] in MODULES:
            module = importlib.reload(MODULES[args[0]])
        else:
            module = importlib.import_module("." + args[0], MODULE_PKG)
            MODULES[args[0]] = module

        if len(args) == 1:
            module.launch()
        else:
            module.launch(args)

    except ModuleNotFoundError:
        print("ERR:  No such module (\"", args[0], "\")", sep="")
    except TypeError as e:
        print("ERR:  ", args[0], ".", e, sep="")


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


def main():
    """The main method.

    Handles the main loop and executes commands by name as passed through the command line.

    Returns:
        None
    """
    print(HEADER)
    while 1:
        i = input(PROMPT).strip().split()
        if not i:
            continue
        elif not COMMANDS.get(i[0]):
            print("ERR:  Command does not exist or is misspelled")
        elif (COMMANDS.get(i[0])[1] != len(i) - 1) and (COMMANDS.get(i[0])[1] != -1):
            print("ERR: Invalid number of args for command ", i[0],
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
    "input": "\033[1;32;40m"  # normal green_text black_background
}
MODULE_PKG = "modules"
COMMANDS = {
        "quit": (quit, 0, "Exit the program"),
        "help": (show_help, 0, "Outputs each command and their description"),
        "about": (info, 0, "Outputs the metadata of the application"),
        "info": (info, 0, "Outputs the metadata of the application"),
        "mod": (launch, -1, "Launches the specified module with the defined args")
    }
METADATA = {
    "Authors": ("Joshua Neighbarger", "Karan Singla", "Zachary Chandler"),
    "App Name": ("NLP Chat Console (Alan)",),
    "Version": ("30 January 2018",)
}
HEADER = METADATA["App Name"][0] + ",  " + METADATA["Version"][0]
PROMPT = ">>>:  "
MODULES = {}

if __name__ == "__main__":
    main()
