"""

This script is a port-knocking utility.
It uses a rotating port system based on a pseudo-blockchain.

Author: Phaide | https://phaide.net/
Licence: GNU GPL v3
Repository: https://github.com/Phaide/port-knocking/
Build: 12/15/2019

"""

# Importing required built-in modules
import socket
from argparse import ArgumentParser
from hashlib import sha3_512
from time import sleep



def write_open_sequence(sequence):
    """
    Formats then writes the sequence to a file
    """
    sequence = "{}, {}, {}".format(sequence[0], sequence[1], sequence[2])
    with open(args.sequenceFile, "w") as sq:
        sq.write(sequence)
        sq.close()
    return

def get_open_sequence():
    """
    Gets a hash from the database's content and deduce a the ports from it
    """
    # Retrieves the content of the databases and hashes it
    dbHash = hash(process_db("read"))
    # Store the new hash to the database
    process_db("append", dbHash, True)
    # Deduce the three ports
    port1 = deduce_port(dbHash)
    port2 = deduce_port(port1)
    port3 = deduce_port(port2)
    return [port1, port2, port3]

def deduce_port(data):
    """
    Deduce a port using the hashing function
    """
    # Iterate through the data
    # The three following lines might not be the most optimized solution, but it's a way to scramble the function's outcome
    if type(data) == "int":
        for x in range(data):
            data += hash(data)
    # Converts the hexdigest to decimal, and reduces it to an acceptable port value using a modulo
    port = int(hex_to_decimal(hash(data)) % args.maxPort)
    # If the deduced port is part of the excludedPorts list (loops while true)
    while port in args.excludedPorts:
        # Append newPort
        port += 1
    return port

def hex_to_decimal(number):
    """
    Converts an hexadecimal value to its decimal equivalent
    """
    # Initiates finalNumber
    finalNumber = 0
    number = str(number)[::-1] # Flips the value
    for index, character in enumerate(number):
        try:
            # Tries to convert the current character to an integer type. Works for values from 0 to 9 included, which are equivalent in both decimal and hexadecimal
            character = int(character)
        except ValueError:
            # Converts an hexadecimal letter to its decimal equivalent
            character = ord(character) - 87
        # Adds to the variable finalNumber the result calculated previously (an integer)
        finalNumber += character*(16**index)
    return finalNumber

def generate_salt(nb):
    """
    Generates a salt of "nb" lenght
    """
    # Import required built-in modules
    from random import SystemRandom
    from string import ascii_uppercase, ascii_lowercase, digits, punctuation
    chars = ascii_uppercase + ascii_lowercase + digits + punctuation
    # Excludes a list of characters from the selection
    bannedChars = ['"', '\\']
    for bannedChar in bannedChars:
        chars = chars.replace(bannedChar, "")
    # Generate the salt
    salt = "".join(SystemRandom().choice(chars) for _ in range(nb))
    return salt

def hash(data):
    """
    Wrapper used to hash data
    """
    # Creates a sha3_512 hash object (from hashlib)
    hash = sha3_512()
    # Adds to the hash object a concatened byte-encoded equivalent of the salt and the data
    hash.update(args.salt.encode() + str(data).encode())
    # Returns the hexadecimal digest (hash)
    return hash.hexdigest()

def process_db(mode, data="", isHashed=False):
    """
    Wrapper for database operations, such as read, write or append.
    """
    # Dictionnary containing accepted modes, and their value equivalent for the open() statement
    acceptedModes = {
        "read": "r+",
        "append": "a",
        "init": "w"
    }
    try:
        # Tries to get the equivalent of an explicit mode (such as "read") and find its open()-allowed equivalent in the above dictionnary ("r+", for "read").
        # Raises KeyError if the mode specified is not in the dictionnary.
        writeMode = acceptedModes[mode]
    except KeyError:
        return
    with open(args.blockchainFile, writeMode) as db:
        if mode == "read":
            # Retrieves database file content
            content = db.read()
            # If the file is empty
            if not content:
                print("The database file is emtpy. Launching initialization.")
                # Launch database initialization
                process_db("init")
                return db.read()
            else:
                return content
        elif mode == "init":
            # Asks user for a keyphrase
            keyphrase = input("Please enter a keyphrase to initiate the database\n> ")
            # Writes the hash of the keyphrase to the database
            db.write(hash(keyphrase))
            input("The database has been initiated. Press enter to escape...")
        else:
            if isHashed == True: # If the data is already hashed
                # Write the unhashed data
                db.write(data)
            else: # Otherwise
                # Hash the data and write it
                db.write(hash(data))
        # Close the file
        db.close()
    return

def send_tcp_packet(port):
    print("Knocking " + str(port))
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set how long before timing out. Needs to be under 1 second for the port-knocking to have any chance of working
    s.settimeout(0.30)
    try:
        # Connect to the server:port
        s.connect((args.server, port))
        # Send some data in a SYN packet
        s.send("")
    except socket.timeout:
        pass
    # Close the socket, thus the connection
    s.close()
    return



# Create an argument parser
parser = ArgumentParser(description='Port-knocking script')

# Add arguments ; change the "default" values to fit your needs
parser.add_argument(
    '--mode',
    choices=['CLIENT', 'SERVER'],
    default="CLIENT",
    type=str,
    help="Specifies which mode to run the script in."
)
parser.add_argument(
    '--closeMode',
    choices=['AUTO', 'MANUAL'],
    default="AUTO",
    type=str,
    help="Specifies wether the close sequence must be sent after waiting (specified by --delay) or after a user input."
)
parser.add_argument(
    '--server',
    default="server.local",
    type=str,
    metavar="ADDRESS",
    help="Server's address ; can be an IPv4, IPv6 or a DNS name."
)
parser.add_argument(
    '--blockchainFile',
    default="blockchain.db",
    type=str,
    metavar="PATH",
    help="Path and name (precise the extension) of the blockchain file ; can be relative or absolute."
)
parser.add_argument(
    '--sequenceFile',
    default="open_sequence",
    type=str,
    metavar="PATH",
    help="Path and name of the file (precise the extension) where the open sequence will be stored ; can be relative or absolute."
)
parser.add_argument(
    '--salt',
    default="tE{DLUe&y]L+r7iL^5y*(X@U1.mkK_LEi9$sUzHuQzB>o(Cj%iO^-v/`.-(&W@XI~1%WVY$xHojXvh+&r|&S2h'u[u1)qR+|f*Q)M[e:)'{O_(;5f0l@C4$2Pkl8QL3?",
    type=str,
    help="Salt to use during the hashing process. You can generate one using --generateSalt."
)
parser.add_argument(
    '--delay',
    default=5,
    type=int,
    help="Time to wait in seconds between the opening and the closing sequences"
)
parser.add_argument(
    '--excludedPorts',
    default=[0, 21, 22, 80, 443],
    type=int,
    nargs="+",
    metavar="PORT",
    help="Lists the ports that shouldn't be used."
)
parser.add_argument(
    '--maxPort',
    default=65536,
    type=int,
    help="Number of ports that can be used (from 0, included)."
)
parser.add_argument(
    '--openSequence',
    type=int,
    nargs=3,
    metavar=("PORT1", "PORT2", "PORT3"),
    help="The three ports used for the open sequence. When specified, doesn't alter the blockchain."
)
parser.add_argument(
    '--closeSequence',
    default=[10000, 20000, 30000],
    type=int,
    nargs=3,
    metavar=("PORT1", "PORT2", "PORT3"),
    help="The three ports used for the close sequence."
)
parser.add_argument(
    '--generateSalt',
    type=int,
    metavar="LENGHT",
    help="Generates a salt of specified lenght and exit."
)

# Retrieves arguments
args = parser.parse_args()



# If the --generateSalt argument is specified
if args.generateSalt:
    # Generate a salt and returns it to the user screen
    input(generate_salt(args.generateSalt))
    # Then exit the script
    exit(0)

# Tries to open a database instance to test if the file exists before proceeding further
try:
    with open(args.blockchainFile, "r+") as db:
        db.close()
except FileNotFoundError:
    input("Database file not found : {0}.\nPlease fix and relaunch...".format(args.blockchainFile))
    exit(404)

# Same for the sequence file
try:
    with open(args.sequenceFile, "r+") as sq:
        sq.close()
except FileNotFoundError:
    input("Sequence file not found : {0}.\nPlease fix and relaunch...".format(args.sequenceFile))
    exit(404)

# Gets the open sequence
openSequence = args.openSequence if args.openSequence else get_open_sequence()



if __name__ == "__main__":
    if args.mode == "CLIENT":
        # Print information note
        input("\nPress enter to run...")
        # Send TCP packets following the open sequence
        for port in openSequence:
            send_tcp_packet(port)
        # If the close mode is set to manual, waits for user input to run the sequence
        if args.closeMode == "MANUAL":
            input("\nPress enter to run the closing process...\n")
        else:
            # Wait for a few seconds
            print("\nWaiting {} seconds before closing...\n".format(args.delay))
            sleep(args.delay)
        print("Launching closing process...\n")
        # Send TCP packets following the close sequence
        for port in args.closeSequence:
            send_tcp_packet(port)
        input("\nPress enter to quit the program...")
    elif args.mode == "SERVER":
        write_open_sequence(openSequence)
    else:
        print("Invalid mode : " + str(args.mode))
