# -*- coding: UTF8 -*-

import inspect

from .core import *
from .utils import *
from .config import Config


class Commands:

    """
    Use this class to add commands to your bot.
    The function name is the command.
    For instance, a function called "call_me" will be executed when the bot receives "/call_me".
    Functions should always be static and return either a string or None.
    Write a docstring that will be used as documentation when calling "/help".
    Once your function is ready to use, add it to the "self.actions" variable, in the __init__() below.
    """

    def __init__(self) -> None:
        # This variable is a dictionary containing for each key (being a valid command) a list of two items:
        # The first is a callback to the associated function
        # The second is a list of arguments. Note: the list is unpacked when calling the function,
        # so each list item is an argument on its own.
        self.actions = {
            "/generate": [Commands.generate, []],
            "/stop": [Commands.stop, []],
            "/start": [Commands.start, []],
            "/help": [Commands.help, [["__init__", "invalid"]]],
        }

    @staticmethod
    def invalid() -> None:
        """
        Function called for every invalid command.
        """
        return

    @staticmethod
    def help(excluded_functions: list) -> str:
        """
        Print this help.
        """
        string = "Commands available: \n\n"
        for func in inspect.getmembers(Commands, predicate=inspect.isfunction):  # func is a 2-tuple.
            if func[0] not in excluded_functions:  # func[0] is a function name.
                string += "/{}: {}\n".format(func[0], inspect.getdoc(getattr(Commands, func[0])))
        return string

    @staticmethod
    def generate() -> str:
        """
        Regenerates the port sequence.
        """

        # If the "use_open_sequence" attribute is set to True, use the specified sequence, otherwise, create a new one.
        if Config.use_open_sequence:
            seq = Config.open_sequence
        else:
            seq = generate_new_sequence()

        # Apply sequence
        set_open_sequence(seq)

        return "New sequence: " + ", ".join(str(p) for p in seq)

    @staticmethod
    def stop() -> str:
        """
        Stops knockd (the listening service).
        """
        stop_service("knockd")
        return "Stopped."

    @staticmethod
    def start() -> str:
        """
        Starts knockd (the listening service).
        """
        start_service("knockd")
        return "Launched."
