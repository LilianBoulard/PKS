# -*- coding: UTF8 -*-

import pks

if not pks.Config.use_open_sequence:
    bot = pks.BotHandler()  # Create a new bot instance

    chan = pks.Channels(bot)
    cmd = pks.Commands(chan)

    message = "New SSH connection registered.\n"
    message += cmd.generate()

    if type(message) == str:
        chan.broadcast(message)

    del bot
