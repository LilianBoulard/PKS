# Port-knocking
A port-knocking utility. 

## Issue
Opening a server publicly to the Internet implies big risks.
Along with different ways of securing this server, such as RSA keys for SSH connections, I learned about a system allowing outside connections "on-demand" using a knocking system, that will open a port once a sequence of packets is send to a series of ports.

A bunch of articles have already been written on the subject, such as this paper, which is relatively interesting :
https://www.sans.org/reading-room/whitepapers/sysadmin/port-knocking-basics-1634

It covers the main problem with port-knocking systems : static port-knocking.

## Solution
This script, written in Python 3, is an attempt to partly solve this issue by dynamically defining new ports using a blockchain-like system.
To reproduce the same behavior on two different computers, the script needs common salt and passphrase.
However, it is far from flawless, and it is not advised for now to use it in a production environment. It's rather an experimental feature.

## Future work
While this is somehow a proof-of-concept version (as of December 2019), a few things can be improved to get it into production state :
- Symmetrically encrypt the database, so that the user needs to enter a password to decrypt it and get the next ports,
- Create different modes for the script to run in : daemon, client/server (actual), server-only (preffered).µ

## Contributing
If you want to contribute, please fork this repo and/or send pull requests. Thank you.
Supporting

You can send me kind messages via my website (https://phaide.net/contact)

Or make a donation to support my work

    BTC: 178oEM3sUYtHVYVt2jbHv4HNjy2nfu1iiT
    ETH: 0x4f3290b22012f0d01900a87e4475c01a7f95ee93

With love,
Phaide.
