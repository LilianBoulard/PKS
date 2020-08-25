# PKS
A Port-Knocking System. 

## Issue
Opening a server publicly to the Internet implies major risks.
\
Along with different ways of securing its access, such as RSA keys for SSH connections, I learned about a system allowing outside connections "on-demand" using a knocking system, that will open a port once a specific sequence of packets is received.

As Wikipedia states it, "Port knocking is a method of externally opening ports on a firewall by generating a connection attempt on a set of prespecified closed ports. 
\
Once a correct sequence of connection attempts is received, the firewall rules are dynamically modified to allow the host which sent the connection attempts to connect over specific port(s)."
These systems provide an additionnal layer of security to a system, but are known for having a critical flaw : static sequences.
Packet sniffing can be used by an attacker to discover the port knock sequences, and therefore get unauthorized access to the server.

## Solution
This system, written in Python 3, is an attempt to solve this issue by dynamically defining new ports sequences.
\
However, it is not flawless ; therefore it is not advised in its current state to use it in a production environment. 
It's rather an experimental feature to build upon.<br />

## Future work
All future work is documented in the "project" section of this repo.
Also, please check "Issues".

## Usage

### Server

*ONLY GNU/LINUX - Only tested on Debian/Ubuntu*

To use the server, you will first need to [get a Telegram bot](https://core.telegram.org/bots#3-how-do-i-create-a-bot).
It's free and very easy !

Next, modify the file `Server/pks/config.py` to fit your needs.

Next, follow [this link](https://www.digitalocean.com/community/tutorials/how-to-use-port-knocking-to-hide-your-ssh-daemon-from-attackers-on-ubuntu) (also available in the docstring of the file `Server/setup.py`) and configure your server by following along the first part (IPTables). Note: be careful when modifying your iptables, espacially if you're connected via SSH.
> Article update : when installing `iptables-persistent`, the service is automatically launched, but you need to configure the saved rules with the command

```bash
cd ~ && touch rules.v4 && sudo iptables-save >> rules.v4 && sudo mv rules.v4 /etc/iptables/
```

Next, update your packages with "sudo apt-get update" (modify to fit your distro) and put the server files in a public directory (such as `/var/app/`) and launch `sudo python3 setup.py`.

Finally, you want to launch the server as a daemon, by opening the root crontab

```bash
sudo crontab -e
```

and adding the line

```bash
@reboot sudo screen -AmdS pku python3 /var/app/run_server.py
```

Reboot, test, and you're good to go !

To manage the PKU server instance, use the command [`screen`](https://help.ubuntu.com/community/Screen).

### Client

*Should work on both Windows and Linux - Only tested on Windows 10*

First, modify the file `Client/pksclient/config.py` to fit your needs.

Next, you need to install the python requirements listed in `Client/requirements.txt`.

To do so, launch the command

```bash
pip install -r requirements.txt
```

And you're good to go !

**Workflow**

The workflow for the client is :
- Configure the PKS client.
- Connect to Telegram, and send `/help` to the bot configured in the server part.
- The list of available commands will appear.
- Send `/generate` to the bot, it will answer a series of ports.
- Prepare your SSH shell (or such), then launch the PKS client, enter the three ports (one by one), and press enter. You will then have about 30 seconds to initiate connection. The port will close itself after this delay.

## Contributing
If you want to contribute, please fork this repo and/or send pull requests. Thank you.<br />

## Supporting
If you want to support me, you can send some kind messages via [my website](https://phaide.net/contact)<br />

And perhaps, consider making a donation<br />

    BTC: 178oEM3sUYtHVYVt2jbHv4HNjy2nfu1iiT
    ETH: 0x4f3290b22012f0d01900a87e4475c01a7f95ee93

With love,<br />
Phaide.
