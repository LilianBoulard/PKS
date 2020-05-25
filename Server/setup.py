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


if not sys.platform.startswith("linux"):
    input("This server can only run on Linux distributions. Press enter to quit...")
    exit()


def knockd_conf(open_sequence_file, close_sequence_file, network_interface, ssh_port):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    return """
[options]
    logfile     = {current_directory}/knockd.log
    interface   = {network_interface}

[opencloseSSH]
    one_time_sequences      = {open_sequence_file}
    seq_timeout             = 5
    start_command           = /sbin/iptables -A INPUT -s %IP% -p tcp --dport {ssh_port} -j ACCEPT
    tcpflags                = syn
    cmd_timeout             = 5
    stop_command            = /sbin/iptables -D INPUT -s %IP% -p tcp --dport {ssh_port} -j ACCEPT

#[closeSSH]
#    one_time_sequences      = {close_sequence_file}
#    seq_timeout             = 5
#    command                 = /sbin/iptables -D INPUT -s %IP% -p tcp --dport {ssh_port} -j ACCEPT
#    tcpflags                = syn

""".format(
        open_sequence_file=open_sequence_file,
        close_sequence_file=close_sequence_file,
        network_interface=network_interface,
        ssh_port=ssh_port,
        current_directory=current_directory,
    )


def install_package(packet_manager, service: str):
    code = int(subprocess.call("sudo {} install {}".format(packet_manager, service), shell=True))
    if code == 0:
        return True
    else:
        return False


def configure_knockd(conf: str) -> None:
    with open(SetupConfig.knockd_config_file, "w") as conf_file:
        conf_file.write(conf)


def main():
    install_package(
        SetupConfig.packet_manager,
        "knockd"
    )
    configure_knockd(
        knockd_conf(
            SetupConfig.close_sequence_file,
            SetupConfig.open_sequence_file,
            SetupConfig.network_interface,
            SetupConfig.ssh_port
        )
    )
    start_service("knockd")
    # subprocess.call("sudo knockd -d", shell=True)


if __name__ == "__main__":
    main()
