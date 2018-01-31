#!/usr/bin/python
# Author: Joshua Neighbarger
# Version: 30 January 2018
# Email: jneigh@uw.edu

""" Example Module

This module is provided as a simple example on the DynamicShell's module lifecycle.
"""


def launch():
    """The only required attribute in each module.

    Returns:
        None
    """
    print("Hello! This is an example module. All modules are launched by the launch function. If it accepts "
          "command-line arguments, they are accepted as a list and is the only parameter to this function.")
