"""

********** IMPORTANT NOTE **********

You must first configure your server following this guide (ONLY THE IPTABLES PART) :

https://www.digitalocean.com/community/tutorials/how-to-use-port-knocking-to-hide-your-ssh-daemon-from-attackers-on-ubuntu

"""

import os
import sys
import subprocess

from pku.config import SetupConfig
from pku.utils import *
from pku.core import *


if not sys.platform.startswith("linux"):
    input("This server can only run on Linux distributions. Press enter to quit...")
    exit()


def install_package(packet_manager, service: str):
    code = int(subprocess.call("sudo {} install {}".format(packet_manager, service), shell=True))
    if code == 0:
        return True
    else:
        return False


def main():
    install_package(
        SetupConfig.packet_manager,
        "knockd"
    )
    configure_knockd(knockd_conf([100, 200, 300]))
    start_service("knockd")


if __name__ == "__main__":
    main()
