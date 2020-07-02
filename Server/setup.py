"""

********** IMPORTANT NOTE **********

You must first configure your server following this guide (ONLY THE IPTABLES PART) :

https://www.digitalocean.com/community/tutorials/how-to-use-port-knocking-to-hide-your-ssh-daemon-from-attackers-on-ubuntu

"""

import sys
import subprocess

from pku.config import Config
from pku.utils import Utils
from pku.core import Core


if not sys.platform.startswith("linux"):
    input("This server can only run on Linux distributions. Press enter to quit...")
    exit()


def main():
    Utils.install_package(
        Config.packet_manager,
        "knockd"
    )
    Core.configure_knockd([100, 200, 300])
    Utils.start_service("knockd")


if __name__ == "__main__":
    main()
