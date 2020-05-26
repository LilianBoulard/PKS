# -*- coding: UTF8 -*-


class Config:

    """
    Class containing the configuration parameters used in the PKU client.
    Each attribute (config variable) is type hinted (constructed as follows):
    variable_name: type = value
    Every variable can handle Python operations, as long as the operation returns the type hinted.
    You can also add static functions that returns values.
    """

    # Remote server to connect to. Can be an IP address or a DNS name.
    server: str = "192.168.0.100"

    # This computer's IP address.
    own_address: str = "192.168.0.48"

    # SSH Port to connect to.
    ssh_port: int = 22

    # Remote username
    username: str = "username"
