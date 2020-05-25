# -*- coding: UTF8 -*-

"""
Main package.
Most of the time, you want to modify "commands.py" instead of this file.
"""

from .telegram import BotHandler
from .commands import Commands
from .config import Config
from . import utils


def main(bot: BotHandler, offset: int = 0) -> None:
    """
    Main loop.
    :param BotHandler bot: a BotHandler object
    :param int offset: Used to filter the messages already processed. Could be used to skip messages.
    :return None:
    """
    utils.log("Launching.")

    utils.start_service("knockd")

    def process(update: dict) -> None:
        """
        Process an update.

        :param dict update: A telegram update.
        :return None:
        """
        utils.log(update)  # Writes the update to the log.

        try:
            chat_text = update['message']['text']  # May raise KeyError for some messages.
        except KeyError:
            chat_text = None

        chat_id = update['message']['chat']['id']
        user_id = update['message']['from']['id']

        # If the whitelist is not empty
        if len(Config.telegram_user_whitelist) > 0:
            if user_id not in Config.telegram_user_whitelist:
                # Terminate if the user is not part of it
                return

        # Terminate if the user is in the blacklist
        if user_id in Config.telegram_user_blacklist:
            return

        choice = chat_text
        commands_o = Commands()
        # From the Commands.actions attribute
        func = commands_o.actions.get(choice, [Commands.invalid])[0]  # Get function
        args = commands_o.actions.get(choice, [None, []])[1]  # Get linked arguments

        # Call the function with its arguments and store the returned value.
        # This value is the response to print to the user.
        message = (func)(*args)

        if type(message) == str:
            bot.send_message(chat_id, message)
    # End of function process

    while True:
        all_updates = bot.get_updates(offset)

        if len(all_updates) > 0:
            for current_update in all_updates:
                first_update_id = current_update['update_id']

                process(current_update)

                offset = first_update_id + 1
