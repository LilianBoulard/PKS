# -*- coding: UTF8 -*-

import pku

if not pku.Config.use_open_sequence:
    bot = pku.BotHandler()  # Create a new bot instance

    chan = pku.Channels(bot)
    cmd = pku.Commands(chan)

    message = "New SSH connection registered.\n"
    message += cmd.generate()

    if type(message) == str:
        chan.broadcast(message)

    del bot
