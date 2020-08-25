# -*- coding: UTF8 -*-

import logging

from .database import Database


class Channels:
    def __init__(self, bot):
        self.bot = bot
        self.db = ChannelsDatabase()

    def add(self, chat_id: str) -> None:
        """
        Adds a new chat id to the known channels database.
        If it already exists, set it to active, otherwise, create it.

        :param str chat_id: A Telegram Chat ID.
        """
        if self.db.channel_exists(chat_id):
            self.db.set_active(chat_id)
        else:
            self.db.add(chat_id)

    def disable(self, chat_id: str) -> None:
        """
        Disables a chat id from the known channels database (only if it exists of course).

        :param str chat_id: A Telegram Chat ID.
        """
        if self.db.channel_exists(chat_id):
            self.db.disable(chat_id)

    def broadcast(self, message: str) -> None:
        """
        Broadcast a message.
        This means a message is sent to every active channel.

        :param str message: The message to broadcast.
        """
        logging.info(f"Broadcasting message: \"{message}\"")
        for chat_id in self.list_active_channels():
            self.bot.send_message(chat_id, message)

    def list_active_channels(self) -> list:
        """
        :return list: A list containing all the active channels.
        """
        column = self.db.query_column(self.db.db_columns[0])
        return [row for row in column if column[row] is True]

    def list_all_channels(self) -> list:
        """
        :return list: A list containing all the channels, active as well as inactive.
        """
        return [chan for chan in self.db.query_column(self.db.db_columns[0])]


class ChannelsDatabase(Database):

    """
    Wrapper used to manipulate the channels database, still roughly low-level.
    Verifications and assertions are done in the `Channels` class.

    Database structure:

    channels = dict{
        channels = {
            "channel_id1": True,
            "channel_id2": False,
        }
    }

    """

    def __init__(self):
        super().__init__(
            "db/channels.db",
            {
                "channels": dict
            }
        )

    def channel_exists(self, chat_id: str) -> bool:
        """
        :param str chat_id: The chat id to search for in the database.
        :return bool: True if the channel id already exists in the database, False otherwise.
        """
        return self.key_exists(self.db_columns[0], chat_id)

    def set_active(self, chat_id: str) -> None:
        """
        Set a channel as active.

        :param str chat_id: A Telegram Chat ID.
        """
        # assert self.key_exists(self.db_columns[0], chat_id)
        self.update(self.db_columns[0], chat_id, True)

    def add(self, chat_id: str) -> None:
        """
        Adds a new chat id to the known channels database.
        Does not care if the chat already exists ; should be checked beforehand.

        :param str chat_id: A Telegram Chat ID.
        """
        self.insert_dict(self.db_columns[0], {chat_id: True})

    def disable(self, chat_id: str) -> None:
        """
        Disables a chat id from the known channels database (removes it from broadcast list).
        Does not care if the chat already exists ; should be checked beforehand.

        :param str chat_id: A Telegram Chat ID.
        """
        # assert self.key_exists(self.db_columns[0], chat_id)
        self.update(self.db_columns[0], chat_id, False)
