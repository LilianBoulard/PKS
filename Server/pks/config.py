# -*- coding: UTF8 -*-


class Config:

    """
    Class containing the configuration parameters used across the PKS project.

    Each attribute (config variable) is type hinted - constructed as follows:
    \
    `variable_name: expected_type = value`

    Variables can handle Python operations.

    You could also add static functions to this class.
    """

    # Token of your bot
    telegram_token: str = ""

    # Maximum time between the moment the user sends a message and when the bot receives it.
    # If a message is received after this delay, it will not be taken into account by the bot.
    # Mainly useful to avoid processing commands sent when the bot was offline.
    telegram_timeout: int = 5

    # Note: to get your Telegram user ID, send "/start" to @userinfobot (via Telegram).

    # A list of telegram userids which should be ADMINISTRATOR of the bot.
    # Needs to be of type string. i.e: ["01234", "56789"]
    # Note: if you're using the whitelist, make sure these admins are part of it.
    telegram_user_admin_list: list = []

    # A list of userids AUTHORIZED to send commands to the bot.
    # Needs to be of type string. i.e: ["01234", "56789"]
    # Watch out: if one or more ids are added to this list, ONLY them will be able to send commands.
    telegram_user_whitelist: list = []
    # A list of userids UNAUTHORIZED to send commands to the bot.
    # Needs to be of type string. i.e: ["01234", "56789"]
    # Can be used alongside the whitelist.
    telegram_user_blacklist: list = []

    # Range of acceptable ports ; first included, last not included (how a usual range works in Python)
    # This variable MUST be a range.
    acceptable_port_range: range = range(1025, 65536)
    # Lists the ports that should not be used.
    # If you want to exclude a range, use this syntax:
    # ports_blacklist: list = [600, 601] + list(range(700, 800))
    ports_blacklist: list = []

    # Port to open and close. Usually, SSH.
    target_port: int = 22

    # Should the script use the following sequence as the open sequence (making the open sequence static).
    # Should only be set to True for tests purposes.
    use_open_sequence: bool = False
    # The ports to use for the open sequence if the above parameter is set to True
    open_sequence: list = [100, 200, 300]

    # How many ports the knocking service uses. In most cases 3.
    sequences_length: int = 3

    # Absolute location of the knockd configuration file.
    knockd_config_file: str = "/etc/knockd.conf"

    # The packet manager of your Linux distro. Working for sure: apt and yum.
    packet_manager: str = "apt"

    # Network interface on which the service must listen.
    network_interface: str = "eth0"
