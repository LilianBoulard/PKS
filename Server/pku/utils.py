# -*- coding: UTF8 -*-

import subprocess
import datetime


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
