# -*- coding: UTF8 -*-


class Config:

    """
    Class containing the configuration parameters used across the PKU project.
    Each attribute (config variable) is type hinted (constructed as follows):
    variable_name: type = value
    Every variable can handle Python operations, as long as the operation returns the type hinted.
    You can also add static functions that returns values.
    """

    # Token of your bot
    telegram_token: str = ""

    # A list of userids AUTHORIZED to send commands to the bot.
    telegram_user_whitelist: list = []
    # A list of userids UNAUTHORIZED to send commands to the bot.
    telegram_user_blacklist: list = []

    # Range of acceptable ports ; first included, last NOT included (how a usual range works)
    # This variable MUST be a range.
    acceptable_port_range: range = range(1025, 65536)
    # Lists the ports that should not be used.
    # If you want to exclude a range, use this kind of syntax:
    # ports_blacklist: list = [500, 600] + list(range(700, 800))
    # I believe you could also use yield and lambda but I didn't test it.
    ports_blacklist: list = []

    # SSH Port, the one to open and close.
    ssh_port: int = 22

    # Sets if the script should use the following sequence as the open sequence (making the open sequence static).
    # If not, generates a new list of ports for the open sequence
    # Should only be set to True for tests purposes.
    use_open_sequence: bool = False
    # The ports to use for the open sequence if the above parameter is set to True
    open_sequence: list = [100, 200, 300]

    # How many ports the knocking service uses. In most cases 3.
    sequences_length: int = 3


class SetupConfig:

    """
    This class is the configuration for setup.py.
    The same rules as the above "Config" class applies.
    """

    # The packet manager of your Linux distro. Working for sure: apt and yum.
    packet_manager: str = "apt"

    # Absolute location of the knockd configuration file.
    knockd_config_file: str = "/etc/knockd.conf"

    # Network interface on which the service must listen.
    network_interface: str = "eth0"

    # See Config.ssh_port
    ssh_port: int = Config.ssh_port
