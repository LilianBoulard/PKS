# Port-knocking
A port-knocking utility. 

## Issue
Opening a server publicly to the Internet implies major risks.<br />
Along with different ways of securing its access, such as RSA keys for SSH connections, I learned about a server-side system allowing outside connections "on-demand" using a knocking system, that will open a port once a specific sequence of packets is received.<br />

A bunch of articles have already been written on the subject, such as this paper, which is pretty interesting and accurate :<br />
https://www.sans.org/reading-room/whitepapers/sysadmin/port-knocking-basics-1634<br />

It covers the main problem with port-knocking systems : static port-knocking.<br />

## Solution
This script, written in Python 3, is an attempt to solve this issue by dynamically defining new ports sequences.<br />
However, it is not flawless ; therefore it is not advised in its current state to use it in a production environment. 
It's rather an experimental feature to build upon.<br />

## Future work
The main thing to rework is the Paramiko shell on the PKU client : when it asks for a password, the user has no choice but to type it in cleartext.

## Usage

### Requirements

**Server**

*ONLY GNU/LINUX - Only tested on Debian/Ubuntu*

To use the server, you will first need to [get a Telegram bot](https://core.telegram.org/bots#3-how-do-i-create-a-bot).
It's easy and free !

Next, modify the file `Server/pku/config.py` to fit your needs.

Next, follow [this link](https://www.digitalocean.com/community/tutorials/how-to-use-port-knocking-to-hide-your-ssh-daemon-from-attackers-on-ubuntu) (also available in the docstring of the file `Server/setup.py`) and configure your server by following along the first part (IPTables ; be careful when modifying your iptables).
> Update of the article : when installing `iptables-persistent`, the service is automatically launched, but you need to configure the saved rules with the command

```bash
cd ~ && touch rules.v4 && sudo iptables-save >> rules.v4 && sudo mv rules.v4 /etc/iptables/
```

Next, put the server files where knockd is authorized to use it (such as `/var/app/`) and launch `setup.py`.

Finally, you want to launch the server as a daemon (somehow) by opening the root crontab

```bash
sudo crontab -e
```

the line

```bash
@reboot sudo python3 /var/app/run_server.py
```

Reboot, test, and you're good to go !

**Client**

*Should work on both Windows and Linux - Only tested on Windows 10*

First, modify the file `Client/pkuclient/config.py` to fit your needs.

Then, the only thing you need to do is to install the requirements listed in the file `Client/requirements.txt`.

To do so, launch the command

```bash
pip install -r requirements.txt
```

And you're good to go ! Next, read the below workflow !

**Workflow**

The workflow for the client is :
- Setup the PKU client.
- Connect to Telegram with your account, and send `/help` to the bot configured in the server part.
- The list of available commands will appear.
- Send `/generate` to the bot, it will answer a series of ports.
- Launch the PKU client, enter the password, the three ports (one by one), press enter, and a SSH shell should open.
- If it doesn't, ask the person in charge of the server to check it is running and the configuration is correct.

***Warning: the shell is emulated by Paramiko. 
The main downside to this approach is that when asked a password, you will have no choice but to type it in cleartext.***

## Contributing
If you want to contribute, please fork this repo and/or send pull requests. Thank you.<br />

## Supporting
If you want to support me, you can send some kind messages via [my website](https://phaide.net/contact)<br />

And perhaps, consider making a donation<br />

    BTC: 178oEM3sUYtHVYVt2jbHv4HNjy2nfu1iiT
    ETH: 0x4f3290b22012f0d01900a87e4475c01a7f95ee93

With love,<br />
Phaide.
