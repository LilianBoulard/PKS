# -*- coding: UTF8 -*-

import sys

import pku


if not sys.platform.startswith("linux"):
    input("This server can only run on Linux distributions. Press enter to quit...")
    exit()

bot = pku.BotHandler()

try:
    pku.main(bot)
except SystemExit:
    del bot
    exit(0)