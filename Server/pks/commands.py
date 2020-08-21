# -*- coding: UTF8 -*-

import inspect
import logging

from functools import wraps

from .permissions import Permissions
from .channels import Channels
from .config import Config
from .utils import Utils
from .core import Core


def permissions_required(*perms):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            obj = args[0]
            if obj.permissions.is_user_allowed(str(obj.user_id), list(perms)):
                result = function(*args, *kwargs)
            else:
                result = "Action forbidden ; insufficient rights."
                logging.info(result + f" User id: {obj.user_id} ; Function called: {function.__name__}")
            return result
        return wrapper
    return decorator


class Commands:

    """

    Use this class to add commands to the telegram bot.

    Please follow these guidelines:
    - The command and the function should be named the same way.
        - For instance if you want to add a command "/call_me", you should add a function to this class named "call_me".
        - As such, Telegram commands should follow functions' naming conventions.
        - The commands of this class and the text commands (those send to the telegram bot) are linked via the
          "commands_l" variable of the __set_commands function of file __init__.
    - Functions must return either a string or nothing (None).
    - The decorator "@permissions_required()" must ALWAYS be present before your function.
        - If everyone should be allowed to launch this command, use "none" as the decorator's argument.
        - The available rights are listed in the attribute "permission_sets" of class Permissions in permissions.py.
        - This decorator can have multiple rights needed for one command. A "AND" operation is performed,
          meaning the user must be granted all of these rights.
    - Write a concise docstring for your function ; it will be used as documentation when calling "/help".
        - This docstring should be a single sentence explaining what the function does.
        - Do not use RST (:param:, :return:, etc).
        - If your function takes used-passed arguments, include a "Usage" line. See function "add_perm" for example.
    - Speaking of arguments, your function can have as many as you want.
        - They are linked using the variable mentioned above.
        - For user-passed args, they must always come last and be in their respective order.
          See function "add_perm" or "remove_perm" for example.
    - If you want to add complex commands, I would advise having a look at files "core.py" and "utils.py".
    - No static function (unless you want to rewrite the bot).
    - Type hinting is good for clarity.

    """

    def __init__(self, chan: Channels):
        self.running = False
        self.permissions = Permissions()
        self.user_id = "1"
        self.permissions.set_telegram_admins()
        self.channels = chan
        self.start()

    def __del__(self):
        self.user_id = "1"
        self.stop()

    @permissions_required("none")
    def invalid(self) -> None:
        """
        Function called for every invalid command.
        """
        return

    @permissions_required("none")
    def help(self, whitelisted_functions: list) -> str:
        """
        Print this help.
        """
        if self.running:
            string = "Commands available: \n\n"
            for func in inspect.getmembers(Commands, predicate=inspect.isfunction):  # func is a 2-tuple.
                function_name = func[0]
                if "/" + function_name in whitelisted_functions:
                    string += "/{}: {}\n".format(function_name, inspect.getdoc(getattr(Commands, function_name)))
            return string

    @permissions_required("manage_sequences")
    def target_port(self) -> str:
        return str(Config.target_port)

    @permissions_required("modify_bot_behaviour", "admin_access")
    def add_perm(self, user: str, group: str) -> str:
        """
        Add a user to a group.
        Usage: /add_perm user group
        """
        if not self.permissions.is_group_valid(group):
            return f"Group {group} is invalid !"
        self.permissions.add_user_to_group(user, group)
        return f"User {user} successfully added to group {group} !"

    @permissions_required("modify_bot_behaviour", "admin_access")
    def remove_perm(self, user: str, group: str) -> str:
        """
        Remove a user from a group.
        Usage: /remove_perm user group
        """
        if not self.permissions.is_group_valid(group):
            return f"Group {group} is invalid !"
        self.permissions.remove_user_from_group(user, group)
        return f"User {user} successfully removed from group {group} !"

    @permissions_required("manage_sequences")
    def generate(self) -> str:
        """
        Regenerates the port sequence.
        """
        # If the "use_open_sequence" attribute is set to True, use the specified sequence,
        # otherwise, create a new one.
        if Config.use_open_sequence:
            seq = Config.open_sequence
        else:
            seq = Core.generate_new_sequence()
        # Apply sequence
        Core.set_open_sequence(seq)
        message = "New sequence: " + ", ".join([str(p) for p in seq])
        if not self.running:
            message += "\nWARNING: the bot is stopped. Start it with /start."
        return message

    @permissions_required("admin_access")
    def status(self) -> str:
        """
        Prints the status of the bot, whether it is running or stopped.
        """
        return "Running" if self.running else "Stopped"

    @permissions_required("admin_access")
    def print_config(self, attr: str or None) -> str:
        """
        Print the config of the bot.
        Usage: /print_config help
        """
        attributes = [d for d in dir(Config) if not d.startswith("__")]
        config = "Value:\n"

        if attr == "help":
            return "Available attributes: all, " + ", ".join(attributes)

        if attr not in attributes:  # If the attribute does not exist
            return "This attribute does not exist. Use \"/print_config help\" or \"/help\" for more information."

        if attr == "all":
            for a in attributes:
                config += getattr(Config, a)  # Get attribute value

        config += getattr(Config, attr)

        return str(config)

    @permissions_required("admin_access")
    def print_broadcast_list(self) -> str:
        """
        Prints a list of IDs corresponding to active channels.
        """
        return ", ".join(self.channels.list_active_channels())

    @permissions_required("modify_bot_behaviour")
    def forget(self, chat_id: str) -> None:
        """
        Remove this channel from the broadcast list.
        """
        self.channels.disable(chat_id)

    @permissions_required("modify_bot_behaviour")
    def list_groups_members(self) -> str:
        """
        Lists all groups memberships.
        """
        message = ""
        for group in self.permissions.get_valid_groups():
            message += group + ": " + ", ".join(self.permissions.get_group_members(group)) + "\n"
        return message

    @permissions_required("modify_bot_behaviour")
    def start(self) -> str:
        """
        Starts knockd. Can be stopped with "/stop".
        """
        if not self.running:
            if not Utils.start_service("knockd"):
                return "Could not start knockd ; unknown error."
            self.running = True
            return "Started knockd."
        else:
            return "Knockd already running."

    @permissions_required("modify_bot_behaviour")
    def stop(self) -> str:
        """
        Stops knockd. Can be restarted with "/start".
        """
        if self.running:
            if not Utils.stop_service("knockd"):
                return "Could not stop knockd ; unknown error."
            self.running = False
            return "Stopped knockd."
        else:
            return "Knockd already stopped."

    @permissions_required("modify_bot_behaviour", "admin_access")
    def shutdown(self):
        """
        Completely stops knockd and the PKS Telegram interface & bot.
        """
        self.stop()
        raise SystemExit
