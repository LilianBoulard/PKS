import requests
import logging
import random

from .config import Config


class BotHandler:
    def __init__(self):
        self.__set_identifier()
        logging.info(f"New instance \"{self.identifier}\" of the Telegram bot created.")
        self.__set_token()
        # Construct API address
        self.api_url = "https://api.telegram.org/bot{}/".format(self.token)

    def __del__(self):
        logging.info(f"Bot instance {self.identifier} destroyed.")

    def __set_identifier(self):
        identifier = ""
        # Creates a new identifier from 6 letters randomly picked between a and z.
        for x in range(6):
            identifier += chr(random.randint(97, 123))
        self.identifier = identifier[0].upper() + identifier[1:]

    def __set_token(self):
        self.token = Config.telegram_token

    def get_updates(self, offset=0, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        try:
            result_json = resp.json()['result']
        except KeyError:
            raise Exception("The Telegram token is invalid. Please check config.py.")
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp
