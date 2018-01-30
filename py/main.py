#!/usr/bin/python
# Author: Joshua Neighbarger
# Version: 30 January 2018
# Email: jneigh@uw.edu

import importlib

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
METADATA = {
    "Authors": ("Joshua Neighbarger", "Karan Singla", "Zachary Chandler"),
    "App Name": ("NLP Chat Console (Alan)",),
    "Version": ("30 January 2018",)
}
HEADER = METADATA["App Name"][0] + ",  " + METADATA["Version"][0]
PROMPT = ">>>:  "


def launch(*args):
    try:
        if not args:
            args = input("What to launch? ").strip().split()
        else:
            args = args[0]
        module = importlib.import_module("." + args[0], MODULE_PKG)
        if len(args) == 1:
            module.launch()
        else:
            module.launch(args)
    except ModuleNotFoundError:
        print("ERR:  No such module (\"", args[0], "\")", sep="")
    except TypeError as e:
        print("ERR:  ", args[0], ".", e, sep="")


def show_help():
    # TODO: Sort headers by key alphabetically
    for cmd in COMMANDS:
        print(cmd, " (", COMMANDS[cmd][1], " args):\t\t", COMMANDS[cmd][2], sep="")


def info():
    for key in METADATA:
        print(key, ":  \t", sep="", end="")
        for value in METADATA[key]:
            print(value, end=",  ")
        print()


def main():
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


if __name__ == "__main__":
    COMMANDS = {
        "quit": (quit, 0, "Exit the program"),
        "help": (show_help, 0, "Outputs each command and their description"),
        "about": (info, 0, "Outputs the metadata of the application"),
        "info": (info, 0, "Outputs the metadata of the application"),
        "mod": (launch, -1, "Launches the specified module with the defined args")
    }
    main()
