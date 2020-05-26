# -*- coding: UTF8 -*-

from hashlib import sha256
from random import randint

from .config import Config
from .utils import *


def generate_new_sequence(num: int = Config.sequences_length, seed: int = None) -> list:
    """
    Generates a new sequence of ports.

    :param int num: How many ports to generate.
    :param int seed: A seed. Two instances of the function using the same seed will return the same ports.
    :return list[int]: A list of ports.

    :example:

    >>> generate_new_sequence()
    [6158, 16499, 8715]

    >>> generate_new_sequence()  # Returns a different list of ports each time it is called.
    [40596, 13335, 5189]

    >>> generate_new_sequence(num=3, seed=123456789)
    [58045, 13282, 10510]

    >>> generate_new_sequence(num=4, seed=123456789)  # Another call, with the same seed
    [58045, 13282, 10510, 3987]

    """

    first_acceptable_port: int = Config.acceptable_port_range[0]
    last_acceptable_port: int = Config.acceptable_port_range[-1:][0]

    if seed:
        port_list = [
            int(
                sha256(
                    str(i + seed).encode("utf-8")
                ).hexdigest(),
                16
            ) for i, _ in enumerate(range(num))
        ]
    else:
        port_list = [
            randint(
                first_acceptable_port,
                last_acceptable_port
            ) for _ in range(num)
        ]

    for i, port in enumerate(port_list):
        while port in Config.ports_blacklist or port not in Config.acceptable_port_range:
            port += 1
            if port > last_acceptable_port:
                port = (port % last_acceptable_port) + first_acceptable_port
            port_list[i] = port

    return port_list


def set_open_sequence(port_sequence: list) -> None:
    """
    Writes the port list to the file specified by the config attribute "open_sequence_file".

    :param list port_sequence: A list containing the ports to write.
    :return None:
    """
    configure_knockd(knockd_conf(port_sequence))

    restart_service("knockd")


def configure_knockd(conf: str) -> None:
    with open(SetupConfig.knockd_config_file, "w") as conf_file:
        conf_file.write(conf)
