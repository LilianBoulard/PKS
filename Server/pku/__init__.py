# -*- coding: UTF8 -*-

"""

Main package.
Most of the time, you want to modify "commands.py" instead of this file.

"""

import logging
import time

from .telegram import BotHandler
from .channels import Channels
from .commands import Commands
from .config import Config


# Setup the configuration for logging.
logging.basicConfig(
    format='%(asctime)s - %(message)s',  # We add a timestamp to each log entries.
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename="/var/log/pku.log",
    filemode="r+",
)


def main(bot: BotHandler, offset: int = 0) -> None:
    """
    Main loop.

    :param BotHandler bot: a telegram bot object
    :param int offset: Used to filter the messages already processed. Could be used to skip messages.
    :return None:

    .. seealso :: run_server.py
    """
    logging.info("Launching.")

    chan = Channels(bot)

    commands_o = Commands(chan)

    def process(update: dict) -> None:
        """
        Process an update.

        :param dict update: A telegram update.
        :return None:
        """
        logging.info(update)

        # This variable is a dictionary containing for each key (being a valid bot command) a tuple of three items:
        # The first is a callback to the associated function from the class Commands (accessible through
        # the object "commands_o").
        # The second is an integer indicating how many arguments are expected FROM THE USER.
        # These user-passed arguments are separated by spaces, such as "/add_perm user group".
        # The third is a list of arguments.
        # Note: this arg list is unpacked when calling the function, so each list item is an argument on its own.
        commands_l = {
            "/generate":
                (commands_o.generate, 0, []),
            "/start":
                (commands_o.start, 0, []),
            "/stop":
                (commands_o.stop, 0, []),
            "/forget":
                (commands_o.forget, 0, [update['message']['chat']['id']]),
            "/shutdown":
                (commands_o.shutdown, 0, []),
            "/list_groups_members":
                (commands_o.list_groups_members, 0, []),
            "/add_perm":
                (commands_o.add_perm, 2, []),
            "/remove_perm":
                (commands_o.remove_perm, 2, []),
        }
        # Adds the "/help" command.
        # Help will only print documentation for the functions listed above (in commands_l).
        commands_l.update({"/help": [commands_o.help, 0, [list(commands_l.keys())]]})

        try:
            chat_text = update['message']['text']  # May raise KeyError for some messages.
        except KeyError:
            chat_text = None

        chat_id = update['message']['chat']['id']
        user_id = update['message']['from']['id']

        # Register the channel by adding it to the broadcast list.
        chan.add(str(chat_id))

        # Set the "user_id" attribute of object "commands_o".
        # It will be used to check if the user is allowed to launch the command.
        commands_o.user_id = user_id

        chat_msg = chat_text.split(" ")

        choice = chat_msg[0]
        func = commands_l.get(choice, [commands_o.invalid])[0]  # Get function
        num_exp_args = commands_l.get(choice, [None, []])[1]  # Get how many arguments should be provided by the user.
        args = commands_l.get(choice, [None, [], []])[2]  # Get additional arguments

        chat_msg.pop(0)  # Removes the command
        original_args_length = len(args)

        for arg in chat_msg:
            args.append(arg)

        found_args = len(args) - original_args_length
        if found_args > num_exp_args:
            message = f"Too many arguments: expected {num_exp_args}, got {found_args}. Please refer to \"/help\"."
        elif found_args < num_exp_args:
            message = f"Too few arguments: expected {num_exp_args}, got {found_args}. Please refer to \"/help\"."
        else:
            # Call the function with its arguments and store the returned value.
            # This value can either be a string (str) or nothing (None).
            message = (func)(*args)

        if type(message) == str:
            bot.send_message(chat_id, message)
    # End of function process

    while True:
        all_updates = bot.get_updates(offset)

        if len(all_updates) > 0:
            for current_update in all_updates:
                try:
                    # Filters the updates: only process the ones who starts with "/".
                    try:
                        upd_txt = current_update['message']['text']  # May raise KeyError for some messages.
                    except KeyError:
                        pass
                    else:
                        upd_time = current_update['message']['date']
                        if upd_txt.startswith("/") and (int(time.time()) - upd_time) < Config.telegram_timeout:
                            process(current_update)
                except SystemExit:
                    del commands_o
                    del chan
                    raise SystemExit

                update_id = current_update['update_id']
                offset = update_id + 1
