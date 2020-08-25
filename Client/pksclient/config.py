# -*- coding: UTF8 -*-


class Config:

    """
    Class containing the configuration parameters used by the PKS client.

    Each attribute (config variable) is type hinted - constructed as follows:
    \
    `variable_name: expected_type = value`

    Variables can handle Python operations.

    You could also add static functions to this class.
    """

    @staticmethod
    def get_interface_from_ip(ipadd) -> str:
        from netifaces import AF_INET
        import netifaces as ni
        for iface in ni.interfaces():
            try:
                for inet in ni.ifaddresses(iface)[AF_INET]:
                    if inet['addr'] == ipadd:
                        return iface
            except KeyError:
                pass
        raise Exception(f"Could not find a network interface with ip {ipadd}. Please verify IP address validity "
                        f"and/or enter the interface name manually.")
    # End of function get_interface_from_ip()

    # Remote server to send packets to. Can be an IP address or a DNS name.
    server: str = "192.168.1.100"

    # This computer's IP address.
    # Should be on the same network as the server's (they should be able to speak to one another).
    # If you are not familiar with TCP/IP, use this tool:
    # http://www.meridianoutpost.com/resources/etools/network/two-ips-on-same-network.php
    own_address: str = "192.168.1.12"

    # Interface from which the packets must originate.
    # Is gathered automatically from the ip address, but you can also enter the right one manually.
    #interface: str = get_interface_from_ip(own_address)

    # Port to connect to.
    target_port: int = 22
