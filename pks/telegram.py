import requests
import logging
import random

from .config import Config


class TelegramBot:

    """

    This class is a production-ready high-level Telegram bot handler.

    It contains actions the bot must do on its own
    (not triggered by users, those are located in the `Commands` class).

    """

    def __init__(self):
        self.__set_identifier()
        logging.info(f"New instance \"{self.identifier}\" of the Telegram bot created.")
        self.__set_token()
        # Construct API address
        self.api_url = f"https://api.telegram.org/bot{self.token}/"
        if not self.__is_token_valid():
            raise ValueError("The Telegram token is invalid. Please check config.py.")

    def __del__(self):
        logging.info(f"Bot instance {self.identifier} destroyed.")

    def __set_identifier(self) -> None:
        """
        Creates a new identifier from 6 letters randomly picked between a and z.
        It is used as a name for the bot instance.
        """
        identifier = ''.join([(chr(random.randint(97, 123))) for _ in range(6)])
        self.identifier = identifier[0].upper() + identifier[1:]

    def __set_token(self) -> None:
        """
        Self explanatory.
        """
        self.token = Config.telegram_token

    def __is_token_valid(self) -> bool:
        """
        Will request the API with the token provided, and, depending on the response, will deduce if it correct.
        :return bool: True if it is, False otherwise.
        """
        r = requests.get(self.api_url)
        if r.json()["description"] != "Not Found":  # The API returns "Unauthorized" when the token is invalid.
            return False
        return True

    def get_updates(self, offset: int = 0, timeout: int = 30) -> dict:
        """
        Get new updates from the API. Essentially, get the new messages.

        :param int offset: (From https://core.telegram.org/bots/api#getupdates).
        Identifier of the first update to be returned.
        Must be greater by one than the highest among the identifiers of previously received updates.
        By default, updates starting with the earliest unconfirmed update are returned.
        An update is considered confirmed as soon as getUpdates is called with an offset higher than its update_id.
        The negative offset can be specified to retrieve updates starting from -
        offset update from the end of the updates queue. All previous updates will be forgotten.
        :param int timeout: (From https://core.telegram.org/bots/api#getupdates).
        Timeout in seconds for long polling.
        Should be positive, short polling should be used for testing purposes only.
        :return dict: The update.
        """
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id: str, text: str, reply_to: str or None = None) -> requests.Response:
        """
        Send a message to a chat_id.

        :param str chat_id: The channel ID into which the message will be sent.
        :param str text: The message to send.
        :param str|None reply_to: Optional. ID of the message to respond to.
        :return requests.Response: A response object.
        """
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}

        if type(reply_to) == int:
            params.update({"reply_to_message_id": reply_to})

        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp
