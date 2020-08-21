# -*- coding: UTF8 -*-

import logging

from hashlib import sha256
from random import randint

from .config import Config
from .utils import Utils


class Core:

    """

    This class contains the most relevant functions in the project, what makes the "core" of the project (haha get it ?)

    Functions which are not core-related should be placed in the Utils class.

    Classes Utils and Core are pretty much the same though.

    All functions in this class should be static.

    """

    @staticmethod
    def generate_new_sequence(num: int = Config.sequences_length, seed: int or None = None) -> list:
        """
        Generates a new sequence of ports.

        :param int num: How many ports to generate.
        :param int seed: A seed used by the generator. Calling the function with a same seed will return the same ports.
        :return list[int]: A list of ports.

        :example:

        >>> Core.generate_new_sequence()
        [6158, 16499, 8715]

        >>> Core.generate_new_sequence()  # Returns a different list each time it is called.
        [40596, 13335, 5189]

        >>> Core.generate_new_sequence(num=3, seed=123456789)
        [58045, 13282, 10510]

        >>> Core.generate_new_sequence(num=4, seed=123456789)  # Another call ; same seed, different length
        [58045, 13282, 10510, 3987]

        """

        logging.debug("Creating a new sequence with args num: int = %s, seed: int = %s.", Config.sequences_length, seed)

        first_acceptable_port: int = Config.acceptable_port_range[0]
        last_acceptable_port: int = Config.acceptable_port_range[-1:][0]

        logging.debug("First acceptable port: %d ; last acceptable port: %d",
                      first_acceptable_port, last_acceptable_port)

        if seed:
            port_list = [
                int(
                    # Hashes the index and the seed.
                    sha256(
                        str(i + seed).encode("utf-8")
                    ).hexdigest(),
                    16  # Converts the hexadecimal digest to decimal.
                ) for i, _ in enumerate(range(num))
            ]
        else:
            port_list = [
                randint(
                    # Applies the range to the randint function
                    first_acceptable_port,
                    last_acceptable_port
                ) for _ in range(num)
            ]

        port_list = Utils.filter_port_list(port_list)

        return port_list

    @staticmethod
    def set_open_sequence(port_sequence: list) -> None:
        """
        Writes a new list of ports to the knockd configuration file.

        :param list port_sequence: A list containing the ports to write.
        """
        Core.configure_knockd(port_sequence)
        Utils.restart_service("knockd")

    @staticmethod
    def configure_knockd(seq: list) -> None:
        """
        Rewrites the knockd configuration file.

        :param list seq: The new sequence to write in the conf.
        """

        def knockd_conf(new_sequence: list) -> str:
            """
            Constructs a new configuration for knockd.

            :param new_sequence: The new sequence to apply to knockd.
            :return str: The new configuration for knockd.
            """
            return """
[options]
    logfile     = /var/log/knockd.log
    interface   = {network_interface}

[opencloseSSH]
    sequence                = {open_sequence}
    seq_timeout             = 5
    start_command           = /sbin/iptables -I INPUT -s %IP% -p tcp --dport {ssh_port} -j ACCEPT
    tcpflags                = syn
    cmd_timeout             = 5
    stop_command            = /sbin/iptables -D INPUT -s %IP% -p tcp --dport {ssh_port} -j ACCEPT
        """.format(
                open_sequence=", ".join([str(p) for p in new_sequence]),
                network_interface=Config.network_interface,
                ssh_port=Config.target_port,
            )
        # End of function knockd_conf()

        with open(Config.knockd_config_file, "w") as conf_file:
            conf_file.write(knockd_conf(seq))
