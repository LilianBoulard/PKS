# -*- coding: UTF8 -*-

import sys

import pks


if not sys.platform.startswith("linux"):
    input("This server can only run on Linux distributions. Press enter to quit...")
    exit()

bot = pks.TelegramBot()

try:
    pks.main(bot)
except SystemExit:
    del bot
    exit(0)