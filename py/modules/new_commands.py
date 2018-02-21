"""NewCommands

This is a test module/plug-in which provides a proof-of-concept of dynamically defined commands and such.

"""


def my_function():
    print("Hello, this is the NewCommands module/plug-in.")


def get_commands():
    return {
        "new_command": (my_function, 0, "Provides a proof-of concept of how a module will be structured.")
    }


def launch():
    pass


def test():
    pass
