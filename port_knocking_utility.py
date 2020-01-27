# coding: utf-8

"""

This script is a port-knocking utility.
It uses different algorithms to create a rotating port system.

Author: Phaide | https://phaide.net/
Licence: GNU GPL v3
Repository: https://github.com/Phaide/port-knocking/
Build: 27/01/2020

"""

# Import required built-in modules
import socket, platform
from argparse import ArgumentParser
from hashlib import sha3_512
from time import sleep
from datetime import datetime
from time import time
from getpass import getpass

try:
    import daemon3x
except ImportError:
    input("The \"daemon3x.py\" file could not be found. PLease download it from github: https://github.com/Phaide/port-knocking/")
    exit()

def install_module(package):
    try:
        if subprocess.check_call([sys.executable, "-m", "pip", "install", package]) == 0:
            return True
    except CalledProcessError as e:
        input("Error encountered while installing package \"{}\" : {}\nPlease install it manually.".format(package, e))
        return False

def send_tcp_packets(portList):
    """
    Sends TCP SYN packets to the sepecified ports.
    Takes a list as argument.
    """
    if type(portList) == list:
        portList = convert_list_elements_to_int(portList, "raise")
        for port in portList:
            # Create a socket object
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Set how long before timing out. Needs to be under 1 second for the port-knocking to have any chance of working
            s.settimeout(float(args.timeout))
            print("Knocking {}".format(port))
            try:
                s.connect((args.server, port))
                # Send some data in a SYN packet
                s.send("")
            except socket.timeout:
                pass
            # Close the socket, thus the connection
            s.close()
    else:
        raise ValueError("Argument portList must be a list, is {}".format(type(portList)))
    return

def deduce_port(data):
    """
    Deduce a port using hashing.
    """
    # Converts the hexdigest to decimal, and reduces it to an acceptable port value using a modulo
    port = int(Encryption.hex_to_decimal(Encryption.hash(data)) % int(args.maxPort))
    # If the deduced port is part of the excludedPorts list (loops while true)
    while port in args.excludedPorts:
        # Append newPort
        port += 1
    return port

def get_open_sequence(openSequenceFile = None):
    """
    Gets a hash from the database's content and deduce the next ports from it
    """
    if openSequenceFile:
        with open(args.sequenceFile, "r+") as sq:
            ports = sq.read()
            sq.close()
        return [int(port) for port in ports.split(", ")]
    else:
        # Retrieves the content of the databases and hashes it
        dbHash = Encryption.hash(process_db("read"))
        # Store the new hash to the database
        process_db("append", dbHash, True)
        # Deduce the three ports
        port1 = deduce_port(dbHash)
        port2 = deduce_port(port1)
        port3 = deduce_port(port2)
        return [port1, port2, port3]

def write_sequence(sequence, limit = 3):
    """
    Writes the sequence to the sequence file.
    Can only take a list as argument.
    """
    if type(sequence) == list and type(limit) == int and len(sequence) == limit:
        with open(args.sequenceFile, "w") as sq:
            sq.write(sequence[0] + "".join([sequence[x + 1] for x in range(limit - 1)]))
            sq.close()
    else:
        raise ValueError("Argument \"sequence\" must be a {}-item list ; is type {} and lenght {}.".format(limit, type(sequence), len(sequence)))
    return

def process_db(mode, data = '', isHashed = False):
    """
    Function used to manage the database.
    "mode" defines which action, accepted values are in the below dictionnary "acceptedModes".
    "data" is the data to append to the database.
    "isHashed" indicates if "data" is hashed.
    """
    # Dictionnary containing accepted modes, and their value equivalent for the open() statement
    acceptedModes = {
        "read": "r+b",
        "append": "ab",
        "init": "wb"
    }
    # Tries to get the equivalent of an explicit mode (such as "read") and find its open()-allowed equivalent in the above dictionnary "acceptedModes" ("r+" for "read").
    # Raises KeyError if the mode specified is not in the dictionnary.
    writeMode = acceptedModes[mode]
    while "checks if the password is 8 bit long":
        if not args.blockchainPassword:
            args.blockchainPassword = args.blockchainPassword if args.blockchainPassword else getpass("Please enter password to use on the pseudo-blockchain file\n>")
        if args.blockchainPassword:
            if len(args.blockchainPassword) != 8:
                print("Invalid key for the blockchain file. Must be 8 bit long, is {}.".format(len(args.blockchainPassword)))
                args.blockchainPassword = None
            else:
                break
    with open(args.blockchainFile, writeMode) as db:
        if mode == "read":
            # Retrieve database file content.
            content = Encryption.manipulate_des("DECRYPT", db.read(), args.blockchainPassword)
            if not content: # If the database file is empty
                print("The database file is emtpy. Launching initialization.")
                # Launch database initialization
                process_db("init")
                process_db(mode, isHashed)
                print("The database has been initialized.")
                # Reads the database again and returns its content.
                return Encryption.manipulate_des("DECRYPT", db.read(), args.blockchainPassword)
            else: # If the database file is not empty
                return content
        elif mode == "init":
            passphrase = Encryption.manipulate_des("ENCRYPT", Encryption.hash(input("Please enter a passphrase to initialize the database\n> ")), args.blockchainPassword)
            db.write(passphrase)
        elif mode == "append":
            if isHashed: # If the data is already hashed
                # Write it to the file
                db.write(Encryption.manipulate_des("ENCRYPT", data, args.blockchainPassword))
            else: # If the data is not hashed
                # Hash then write it
                db.write(Encryption.manipulate_des("ENCRYPT", Encryption.hash(data), args.blockchainPassword))
        # Close the file
        db.close()
    return

def convert_list_elements_to_int(uList, failMode = 'pass'):
    """
    Tries to convert every items of a list to integers.
    """
    if type(uList) == list:
        for index, element in enumerate(uList):
            try:
                # Convert item to integer
                uList[index] = int(element)
            except ValueError: # Error handling
                print("Failed to convert {} into integer.".format(element))
                if failMode == "pop":
                    print("Removing list element.")
                    uList.pop(index)
                    pass
                elif failMode == "stop":
                    print("Stopping")
                    return uList
                elif failMode == "raise":
                    raise Exception
                else:
                    print("Passing.")
                    pass
    else: # If the variable uList is not a list
        raise TypeError("Invalid type for variable uList: must be list, is {}".format(type(uList)))
    return uList

def convert_str_to_list(strLst, convertElementsToInt = True):
    """
    Takes as paramter a list in a string, like "[1, 2, 3]" and converts it to a list type.
    """
    if type(strLst) == str:
        # Remove the brackets then split the string.
        strLst = strLst.replace("[", "").replace("]", "").split(",")
    elif type(strLst) == list:
        # Returns the list if its type is already list.
        pass
    else:
        raise TypeError("Invalid type given for argument strLst. Must be str or list, is {}.".format(type(strLst)))
    return strLst

def merge_args(newArgs):
    """
    Merges the already set args (stored in the global variable "args") with new ones.
    Merging is exclusive (already set arguments will not be replaced by new ones).
    The highest priority goes to user input, then config file, then default args.
    """
    # Gets a dictionnary type mirror of the global variable "args". Making modification on this dictionnary will modify the original Namespace.
    dict_args = vars(args)
    for arg in newArgs:
        try:
            # This if loop will raise a KeyError if the value doesn't exist in the arguments.
            if not dict_args[arg]:
                dict_args[arg] = newArgs[arg]
        except KeyError:
            print("WARNING: Invalid argument in config file : {}".format(arg))
            pass

class Client:
    def get_remote_value(self, ssh, command, valueName, nargs = 1):
        """
        Gets a value from a remote computer using SSH.
        """
        # Execute command and gets the std values.
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
        # Expand stdout and stderr
        ssh_stdout, ssh_stderr = ssh_stdout.readlines(), ssh_stderr.readlines()
        global remoteValues
        # If the commands raised errors
        if ssh_stderr != []:
            # Print them to the screen
            print([line.rstrip() for line in ssh_stderr])
            # And sets the value to ERROR
            remoteValues[valueName] = "ERROR"
        else:
            # Initiate the content
            content = ""
            # For every line in the stdout
            for index, out in enumerate(ssh_stdout):
                # nargs is used here to tell how many lines from the stdout we want to keep
                if index < nargs:
                    content += out.rstrip()
                else:
                    break;
            remoteValues[valueName] = content
        return

    def get_sequence_from_server(self):
        """
        Connect to the server in SSH, search for the open sequence file, get its content and writes it on the client system.
        """
        from subprocess import call
        try: # We try to import the needed module
            import paramiko
        except ImportError: # If the module is not found
            # We try to install it
            call('pip install paramiko', shell = True)
            try:
                # We try to import it again
                import paramiko
            except: # If it couldn't, close the program
                input("The paramiko module couldn't be installed. Please try to install it with this command : [PATH]/python.exe -m pip install paramiko")
                return
        # Create SSH client object
        ssh = paramiko.SSHClient()
        # Import known hosts
        ssh.load_system_host_keys()
        # If the host is unknown, add it to the known host list
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Set the number of attempts before giving up
        connectionAttempts = 3
        # Default arguments to pass to the "ssh.connect()"
        sshArguments = {
            "username": args.sshRemoteUsername,
            "port": args.sshRemotePort,
            "timeout": args.sshConnectionTimeout
        }
        if args.sshPrivateKeyFile:
            # Asks for the private key if none is set
            args.sshPrivateKeyPassword = args.sshPrivateKeyPassword if args.sshPrivateKeyPassword else getpass("Enter the passphrase of the private key (leave empty if none is set) : ")
            try:
                # Add the private key to the argument list
                sshArguments["pkey"] = paramiko.RSAKey.from_private_key_file(args.sshPrivateKeyFile, args.sshPrivateKeyPassword)
            except IOError:
                print("Couldn't read the private key {}".format(args.sshPrivateKeyFile))
                return
            except paramiko.ssh_exception.SSHException as e: # Catch any other errors
                print(e)
                return
            args.sshRemotePassword = args.sshRemotePassword if args.sshRemotePassword else ""
        else:
            args.sshRemotePassword = args.sshRemotePassword if args.sshRemotePassword else getpass("Please enter SSH password:")
        # Add the SSH password to the arguments to pass
        sshArguments["password"] = args.sshRemotePassword
        for x in range(connectionAttempts):
            try:
                # Connect to the server
                ssh.connect(args.server, **sshArguments)
                # Remove the variables references
                del args.sshRemotePassword
                del args.sshPrivateKeyPassword
                # Break the for loop
                break
            except paramiko.ssh_exception.AuthenticationException: # Wrong password
                print("Permission denied, please try again.")
                args.sshRemotePassword = getpass("Please enter SSH password:")
                pass
            except paramiko.ssh_exception.BadHostKeyException: # Catching bad host key exception (if the server's key is different from the known one)
                print("Host key could not be verified ; CAREFUL : the sever may have been compromised !\nAborting")
                # Set close mode to manual, so that the access doesn't close automatically.
                args.closeMode = "MANUAL"
                return
            except socket.timeout: # Catching time out exception
                print("Timed out after {} seconds.".format(args.sshConnectionTimeout))
            except paramiko.ssh_exception.SSHException as e: # Catching any other exception
                input("Error while connecting: {}".format(e))
                pass
            finally:
                if x == (connectionAttempts - 1):
                    input("Failed connecting. You have to connect manually and get the closing sequence manually. Closing mode switched to manual.")
                    # Set close mode to manual, so that the access doesn't close automatically.
                    args.closeMode = "MANUAL"
                    return
        global remoteValues
        # Init remote value dictionnary
        remoteValues = {}
        # Get remote operating system using a Python command
        self.get_remote_value(ssh, 'python3 -c "import platform; print(platform.system());"', "operatingSystem")
        if remoteValues["operatingSystem"] == "Linux":
            # Get the path to the open sequence file
            self.get_remote_value(ssh, 'locate {}'.format(args.sshRemoteOpenSequenceFileName), "openSequenceFileLocation")
            # Gathers the content of the previously found file. Using sudo in this case, might not be needed.
            self.get_remote_value(ssh, 'cat {}'.format(remoteValues["openSequenceFileLocation"]), "openSequenceFileContent")
        elif remoteValues["operatingSystem"] == "Windows":
            # Get the path to the open sequence file using PowerShell
            self.get_remote_value(ssh, 'powershell "Get-Childitem -Path C: -Filter {} -ErrorAction Ignore -File -Recurse | % { $_.FullName }"'.format(args.sshRemoteOpenSequenceFileName), "openSequenceFileLocation")
            # Gathers the content of the previously found file using PowerShell
            self.get_remote_value(ssh, 'powershell cat "{}"'.format(remoteValues["openSequenceFileLocation"]), "openSequenceFileContent")
        elif remoteValues["operatingSystem"] == "ERROR":
            print("Couldn't find remote computer's OS.")
        else:
            print("The remote OS is not supported : {}".format(remoteValues["operatingSystem"]))
        # Close the SSH connection
        ssh.close()
        # Check if some values could not be obtained
        if remoteValues["openSequenceFileLocation"] in ("ERROR", ""):
            print("Couldn't get remote file \"{}\" location.".format(args.sshRemoteOpenSequenceFileName))
            #return
        if remoteValues["openSequenceFileContent"] in ("ERROR", ""):
            print("Couldn't get content of remote file \"{}\": does not exist, or is empty.".format(remoteValues["openSequenceFileLocation"]))
            #return
        # Now that we have the file's content, we can check if it corresponds to a valid sequence
        try:
            # Format the content of the file to an integer list
            openSequence = convert_list_elements_to_int(remoteValues["openSequenceFileContent"].split(","), "raise")
            # Check if the ports are valid (lower than maxPort)
            for port in openSequence:
                if port >= args.maxPort:
                    print("Invalid port : {}".format(port))
                    raise Exception
            # Write the ports to the sequence file.
            # The function "write_sequence" will raise an error if the list is not composed of 3 items
            write_sequence(openSequence)
            print("Wrote {} successfully with the three next ports : {}".format(args.sequenceFile, openSequence))
            pass
        except:
            input("The content of file \"{}\" ({}) is not format expected for an open sequence.\nFormat needed is \"PORT, PORT, PORT\".".format(remoteValues["openSequenceFileLocation"], remoteValues["openSequenceFileContent"]))
            print(remoteValues)

class Server(daemon3x.Daemon):
    def get_sleep_time(self):
        """
        Returns the time left (in seconds) before the next round hour.
        Change this function if you need the script to support a regeneration interval greater than 3600 seconds.
        """
        return args.regenerationInterval - (datetime.now().second + (datetime.now().minute * 60))

    def restart_service(self, service, utility = "systemctl"):
        """
        Used to restart the service responsible of analyzing the firewall logs (usually iptables or knockd).
        """
        from subprocess import call
        if utility == "systemctl":
            command = "sudo {} restart {}".format(utility, service)
        elif utility == "service":
            command = "sudo {} {} restart".format(utility, service)
        call(command, shell = True)
        return

    def run(self):
        """
        Code that the daemon will execute.
        """
        now = datetime.now()
        port1 = deduce_port(((now.hour ** now.day) * now.year) ** now.month)
        port2 = deduce_port(port1 ** now.hour)
        port3 = deduce_port(port3 ** now.hour)
        write_sequence([port1, port2, port3])
        self.restart_service(args.FirewallLogParserService)
        # Sleep until the next hour
        sleep(self.get_sleep_time())

class XML:
    def get_xml_config(configFile):
        """
        Parse an XML config file to get contained arguments.
        """
        from xml.etree import ElementTree
        fileArgs = {}
        try:
            # Parse configFile content
            for child in ElementTree.parse(configFile).getroot():
                try:
                    # Add a line to the dictionnary
                    fileArgs[child.attrib["id"]] = child.attrib["value"]
                except AttributeError as e:
                    input("XML error: {} {}".format(child.attrib, e))
        except FileNotFoundError:
            print("Could not import XML config file : {}\nUsing default settings.".format(configFile))
            return {}
        except ElementTree.ParseError as e:
            print("Invalid XML config file.\n{}\nUsing default settings.".format(e, configFile))
            return {}
        return fileArgs

    def generate_xml_config(configPath, xmlVersion = "1.0", xmlEncoding = "UTF-8"):
        """
        Generates an XML config file using the default args.
        """
        try:
            with open(configPath, "w") as cfg:
                cfg.write("<?xml version=\"{}\" encoding=\"{}\"?>\n\n<args>\n".format(xmlVersion, xmlEncoding))
                for arg in defaultArgs:
                    cfg.write("    <arg id=\"{}\" value=\"{}\" />\n".format(arg, defaultArgs[arg]))
                cfg.write("</args>\n")
                cfg.close()
            input("Sample config file generated successfully at {}\nPress enter to quit...".format(configPath))
        except FileNotFoundError:
            input("Invalid name for config file : {}\nPress enter to quit...".format(configPath))
            pass
        return

class Encryption:
    def generate_salt(nb):
        """
        Generates a salt of "nb" lenght.
        """
        # Import required built-in modules
        from random import SystemRandom
        from string import ascii_uppercase, ascii_lowercase, digits, punctuation
        # Aggregate characters types in a variable
        chars = ascii_uppercase + ascii_lowercase + digits + punctuation
        print("Excluded characters : {}".format(args.saltExcludedChars))
        # Generate the salt with inline for loop and ternary conditional operator
        return "".join(SystemRandom().choice(chars if chars not in args.saltExcludedChars else "_") for _ in range(nb))

    def hash(data):
        """
        Wrapper used to hash "data".
        Uses a salt to improve hash security.
        """
        data = data if type(data) == bytes else str(data).encode(charset)
        # Creates a sha3_512 hash object and adds to it the aggregated byte-encoded data and salt
        hash = sha3_512(data + args.salt.encode())
        # Returns the hexadecimal digest (hash)
        return hash.hexdigest()

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

    def manipulate_des(mode, data, key):
        """
        Wrapper used to manipulate DES encryption, using pyDes module.
        Documentation : http://whitemans.ca/des.html
        """
        try:
            import pyDes
        except ImportError:
            install_module("pyDes")
            import pyDes
        # Converts data to bytes if it is not already
        data = data if type(data) == bytes else str(data).encode(charset)
        # Sets which padmode to use
        padmode = pyDes.PAD_PKCS5
        # Creates a DES key
        k = pyDes.des(key.encode(charset), pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=padmode)
        # Returns the encoded or decoded text
        if mode == "ENCRYPT":
            return k.encrypt(data, padmode=padmode)
        elif mode == "DECRYPT":
            return k.decrypt(data, padmode=padmode)



# Create an argument parser
parser = ArgumentParser(description = 'Port-knocking utility')

# Add arguments ; DO NOT add "default" values. Instead, use the dictionnary under this section.
# The "default" argument is not used because this way we can set priorities between user input and default values.
parser.add_argument(
    '--mode',
    choices = ['CLIENT', 'SERVER', "LIGHTCLIENT"],
    type = str,
    help = "Specifies which mode to run the script in."
)
parser.add_argument(
    '--closeMode',
    choices = ['AUTO', 'MANUAL'],
    type = str,
    help="Specifies wether the close sequence must be sent after waiting (specified by --delay) or after a user input."
)
parser.add_argument(
    '--server',
    type = str,
    metavar = "ADDRESS",
    help = "Server's address ; can be an IPv4, IPv6 or a DNS name."
)
parser.add_argument(
    '--blockchainFile',
    type = str,
    metavar = "PATH",
    help = "Path and name (precise its extension) of the blockchain file ; can be relative or absolute."
)
parser.add_argument(
    '--blockchainPassword',
    type = str,
    metavar = "PASSWORD",
    help = "Password used to encrypt and decrypt the database. It will be asked if the argument is not set."
)
parser.add_argument(
    '--sequenceFile',
    type = str,
    metavar = "PATH",
    help = "Path and name (precise its extension) of the open sequence file (where the open sequence will be stored) ; can be relative or absolute."
)
parser.add_argument(
    '--salt',
    type = str,
    help = "Salt used during the hashing process. You can generate one using --generateSalt."
)
parser.add_argument(
    '--delay',
    type = int,
    metavar = "TIME",
    help = "Time to wait in seconds between the opening and the closing sequences"
)
parser.add_argument(
    '--timeout',
    type = float,
    metavar = "TIME",
    help = "Floating number specifying the time to wait before the TCP connection times out. Must be less than a second."
)
parser.add_argument(
    '--excludedPorts',
    type = int,
    nargs = "+",
    metavar = "PORT",
    help = "Lists the ports that shouldn't be used."
)
parser.add_argument(
    '--maxPort',
    type = int,
    help = "Number of ports that can be used (0 included)."
)
parser.add_argument(
    '--openSequence',
    type = int,
    nargs = 3,
    metavar = ("PORT1", "PORT2", "PORT3"),
    help = "The three ports used for the open sequence. When specified, doesn't alter the blockchain file."
)
parser.add_argument(
    '--closeSequence',
    type = int,
    nargs = 3,
    metavar = ("PORT1", "PORT2", "PORT3"),
    help = "The three ports used for the close sequence."
)
parser.add_argument(
    '--regenerationInterval',
    type = int,
    metavar = "SECONDS",
    help = "Time the daemon will wait between each port generation. By default, an hour (should stay that way : the script is not designed to support more the 3600 seconds)"
)
parser.add_argument(
    '--sshRemoteUsername',
    type = str,
    metavar = "USERNAME",
    help = "Name of the user account used for SSH connection to the server."
)
parser.add_argument(
    '--sshRemotePassword',
    type = str,
    metavar = "PASSWORD",
    help = "Password of the user account used for SSH connection. It will be asked if the parameter is not set."
)
parser.add_argument(
    '--sshRemotePort',
    type = int,
    metavar = "PORT",
    help = "Remote SSH port to connect to. Default is 22."
)
parser.add_argument(
    '--sshRemoteOpenSequenceFile',
    type = str,
    metavar = "FILENAME",
    help = "Name of the remote open sequence file to look for (do not include the path, but precise its extension)."
)
parser.add_argument(
    '--sshConnectionTimeout',
    type = int,
    metavar = "TIME",
    help = "SSH connection timeout, in seconds."
)
parser.add_argument(
    '--sshPrivateKeyFile',
    type = str,
    metavar = "PATH",
    help = "Path and name (precise its extension) of the SSH private key file ; can be relative or absolute."
)
parser.add_argument(
    '--sshPrivateKeyPassword',
    type = str,
    metavar = "PASSWORD",
    help = "Password of the private key. It will be asked if the argument is not set and a private key file is precised."
)
parser.add_argument(
    '--FirewallLogParserService',
    type = str,
    metavar = "SERVICE",
    help = "Name of the service used on the remote Linux server to parse firewall logs. Usually it's knockd (default) or iptables."
)
parser.add_argument(
    '--configFile',
    metavar = "PATH",
    help = "Path and name (precise its extension) of an XML config file ; can be relative or absolute. Use --generateConfigFile to create one."
)
parser.add_argument(
    '--generateConfigFile',
    type = str,
    metavar = "PATH",
    help = "Generates a sample XML config file. Takes as parameter the path and name (precise its extension) of the file ; can be relative or absolute."
)
parser.add_argument(
    '--generateSalt',
    type = int,
    metavar = "LENGHT",
    help = "Generates a salt of specified lenght, then exit."
)
parser.add_argument(
    '--saltExcludedChars',
    nargs = "+",
    metavar = "\"CHAR\"",
    help = "Used along --generateSalt, specifies a list of characters that must be excluded from the salt. [NOT OPERATIONAL]"
)

# Retrieves arguments
args = parser.parse_args()



# If the --generateSalt argument is specified
if args.generateSalt:
    # Generate a salt and returns it to the user screen
    input(Encryption.generate_salt(args.generateSalt))
    # Then exit the script
    exit(0)

defaultArgs = {
    "mode": "CLIENT",
    "closeMode": "AUTO",
    "server": "192.168.0.100",
    "blockchainFile": "blockchain.db",
    "sequenceFile": "open_sequence",
    # Following salt should not include these characters : ", \ and & (even escaped)
    # The recommended salt lenght should be 128 bits (source : https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-132.pdf)
    "salt": "tE{DLUe_y]L+r7iL^5y*(X@U1.mkK_LEi9$sUzHuQzB>o(Cj%iO^-v/`.-(_W@XI~1%WVY$xHojXvh+_r|_S2h'u[u1)qR+|f*Q)M[e:)'{O_(;5f0l@C4$2Pkl8QL3?",
    "delay": 5,
    "timeout": 0.30,
    "maxPort": 65536,
    "regenerationInterval": 3600,
    "closeSequence": [5008, 25089, 11986],
    "saltExcludedChars": [],
    "sshRemoteUsername": "anonymous",
    "sshRemotePort": 22,
    "sshRemoteOpenSequenceFile": "open_sequence",
    "sshConnectionTimeout": 1,
    "FirewallLogParserService": "knockd"
}

if args.generateConfigFile:
    XML.generate_xml_config(args.generateConfigFile)
    exit()

if args.configFile:
    merge_args(XML.get_xml_config(args.configFile))

merge_args(defaultArgs)



# Tries to open required files to test if they exists before proceeding further
for filePath in [args.blockchainFile, args.sequenceFile, args.sshPrivateKeyFile]:
    if filePath != None:
        try:
            with open(filePath, "r+") as fl:
                fl.close()
        except FileNotFoundError:
            print("File not found : " + filePath)
            # Create the file if not found
            with open(filePath, "w") as fl:
                fl.close()
            print("Created.")

# List of excluded ports, that should not be used. Modify below list with ports that should be excluded by default.
defaultExcludedPorts = [0, 21, 22, 80, 443]
args.excludedPorts = defaultExcludedPorts + args.excludedPorts if args.excludedPorts else defaultExcludedPorts
print("Excluded ports : {}".format(args.excludedPorts))

# Sets the charset used by the script
charset = "utf-8"

args.closeSequence = convert_str_to_list(args.closeSequence)

# Gets the open sequence
openSequence = convert_str_to_list(args.openSequence if args.openSequence else get_open_sequence() if args.mode != "LIGHTCLIENT" else get_open_sequence(args.sequenceFile))



if args.mode == "CLIENT" or args.mode == "LIGHTCLIENT":
    send_tcp_packets(openSequence)
    if args.mode == "LIGHTCLIENT":
        Client.get_sequence_from_server()
    # If the close mode is set to manual, waits for user input to run the sequence
    if args.closeMode == "MANUAL":
        input("\nPress enter to run the closing process...\n")
    else:
        print("\nWaiting {} seconds before closing...\n".format(args.delay))
        sleep(float(args.delay))
    print("Launching closing process...\n")
    send_tcp_packets(args.closeSequence)
    input("\nPress enter to quit the program...")
elif args.mode == "SERVER":
    write_sequence(openSequence)
elif args.mode == "DAEMON":
    if platform.system() == "Linux":
        try:
            Server.start()
        except KeyboardInterrupt:
            Server.stop()
else:
    print("Invalid mode : " + str(args.mode))
