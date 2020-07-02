# -*- coding: UTF8 -*-


class Config:

    """
    Class containing the configuration parameters used across the PKU project.
    Each attribute (config variable) is type hinted - constructed as follows:
    variable_name: expected_type = value
    Variables can handle Python operations, as long as they return the type hinted.
    You could also add static functions to this class that returns values.
    """

    # Token of your bot
    telegram_token: str = ""

    # Maximum time in seconds between user sending a message and the server receiving it.
    telegram_timeout: int = 5

    # Note : to get your Telegram user ID, send "/start" to @userinfobot (via Telegram).

    # A list of userids AUTHORIZED to send commands to the bot.
    # Watch out: if one or more ids are added to this list, ONLY them will be able to send commands.
    telegram_user_whitelist: list = []
    # A list of userids UNAUTHORIZED to send commands to the bot.
    # Can be used alongside the whitelist.
    telegram_user_blacklist: list = []

    # A list of telegram userids which should be ADMINISTRATOR of the bot.
    # Note: if you're using the whitelist, make sure these admins are part of it.
    telegram_user_admin_list: list = []

    # Range of acceptable ports ; first included, last NOT included (how a usual range works)
    # This variable MUST be a range.
    acceptable_port_range: range = range(1025, 65536)
    # Lists the ports that should not be used.
    # If you want to exclude a range, use this kind of syntax:
    #ports_blacklist: list = [500, 600] + list(range(700, 800))
    ports_blacklist: list = []

    # SSH Port, the one to open and close.
    ssh_port: int = 22

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
