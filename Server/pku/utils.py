# -*- coding: UTF8 -*-

import subprocess
import datetime

from .config import SetupConfig


def log(message) -> None:
    """
    :param message: Data to log. Can be any object that supports __str__().
    :return None:
    """
    print(datetime.datetime.now(), message)


def start_service(service: str) -> bool:
    code = int(subprocess.call("sudo systemctl start " + service, shell=True))
    if code == 0:
        return True
    else:
        return False


def stop_service(service: str) -> bool:
    code = int(subprocess.call("sudo systemctl stop " + service, shell=True))
    if code == 0:
        return True
    else:
        return False


def restart_service(service: str) -> bool:
    if stop_service(service) and start_service(service):
        return True
    else:
        return False


def knockd_conf(new_sequence: list) -> str:
    """
    :param new_sequence: A list containing the new sequence to apply to knockd.
    :return str: The new configuration for knockd, string format.
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
        network_interface=SetupConfig.network_interface,
        ssh_port=SetupConfig.ssh_port,
    )
