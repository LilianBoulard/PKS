# -*- coding: UTF8 -*-

from getpass import getpass

from scapy.all import *
from time import sleep

import paramiko

from . import interactive
from .config import Config


def send_tcp_packet(server: str, port: int) -> None:
    """
    Send a TCP SYN packet to the specified server:port.

    :param str server:
    :param int port:
    :return None:
    """
    src_port = port
    dst_port = port
    src = "192.168.0.48"
    dst = server
    ip = IP(src=src, dst=dst)
    syn = TCP(sport=src_port, dport=dst_port, flags='S', seq=1000)
    send(ip / syn)


def main():
    password = getpass("Please enter the password of this account (leave empty if you have RSA keys configured):\n> ")

    ports = [int(input("Please enter {} port:\n>".format(n))) for n in ["first", "second", "third"]]

    for port in ports:
        send_tcp_packet(Config.server, port)
        sleep(0.1)

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for i in range(3):  # Loop used to ask the user the password again if the previous one is incorrect.
        try:
            ssh.connect(Config.server, username=Config.username, password=password, port=Config.ssh_port)
        except paramiko.ssh_exception.AuthenticationException:
            password = getpass("The password is incorrect. Please try again:\n> ")
        except Exception as exc:
            print(exc)
            return
        else:
            break

    chan = ssh.invoke_shell()

    try:
        interactive.interactive_shell(chan)
    except OSError:
        # The interactive shell script raises OSErrors on some occasions. Usually when sending "exit" to bash.
        pass

    chan.close()
    ssh.close()

