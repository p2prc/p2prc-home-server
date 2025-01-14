import ctypes
from ctypes import Structure, c_char_p, c_int, cdll
from dataclasses import dataclass, astuple
import time
import json
from urllib.parse import urlparse
from typing import List
import subprocess
import uuid
import dacite
import os
import sqlalchemy
import dataclasses
from typing import Union
import schedule
import threading
import requests
from pathlib import Path
import platform

# # Create Sqlite database to track processes 
# engine=sqlalchemy.create_engine(f'sqlite:///homeserver.db')

# Global variable 
# A global variable will be populated on runtime.
# It is read from P2PRC directly or from a local
# database. 

print(platform.system().lower() + "-" + platform.machine().lower())

match platform.system().lower() + "-" + platform.machine().lower():
    case "darwin-arm64":
        lib_path = Path(__file__).parent.parent / "lib" / "darwin-arm64" / "p2prc.so"

print(str(lib_path))
p2prc = ctypes.CDLL(str(lib_path))

p2prc.Init("")

print("main called")

# Start running schedule
schedule.run_pending()

# Run the track processes every 3 seconds 
# schedule.every(3).seconds.do(BackgroundTrackProcess)

Background_track_thread = threading.Thread(target=BackgroundTrackProcess, name="Track Process")
# Kills the tread of system exit
Background_track_thread.setDaemon(True)
Background_track_thread.start()
            

# Node information
# Generated using: https://jsonformatter.org/json-to-python
@dataclass
class Node:
    Name: str
    MachineUsername: str
    IPV4: str
    IPV6: str
    Latency: int
    Download: int
    Upload: int
    ServerPort: str
    BareMetalSSHPort: str
    NAT: str
    EscapeImplementation: str
    ProxyServer: str
    UnSafeMode: bool
    PublicKey: str
    CustomInformation: str

@dataclass
class IPAddress:
    ip_address: List[Node]


# ----------------------------------------------------------------------------
# ----------------------------- Helper functions ----------------------------- 
# ----------------------------------------------------------------------------  

def StartServer():
    # Starting P2PRC as a server mode
    p2prc.Server()
    # for _ in iter(int, 1):
    #     pass

# Class to create string to pass as string function 
# parameter to shared object file
class go_string(Structure):
    _fields_ = [
    ("p", c_char_p),
    ("n", c_int)]

# Local port intended to ensure that 
def P2PRCMapPort(port="",domainname="",serveraddress=""):
    # Local Port intended to be escaped outside NAT
    # Converting to the appropirate datatype to be
    # passed as a string to GoLang.
    port = go_string(c_char_p(port.encode('utf-8')), len(port))
    domainname = go_string(c_char_p(domainname.encode('utf-8')), len(domainname))
    serveraddress = go_string(c_char_p(serveraddress.encode('utf-8')), len(serveraddress))

    # Defining the response type of the GoLang function 
    # function
    p2prc.MapPort.restype = c_char_p
    # Calling the Go function
    address = p2prc.MapPort(port,domainname,serveraddress)
    res = str(address).strip("b'")
    return res

def ListNodes():
    # View IP Table information 
    p2prc.ViewIPTable.restype = c_char_p
    ipTable = p2prc.ViewIPTable()
    # View IP Table as 
    ipTableObject = json.loads((str(ipTable).strip("b'")))
    dat: IPAddress = dacite.from_dict(IPAddress,ipTableObject)
    return dat

# -----------------------------------------------------------------------------------
# ----------------------------- End of helper functions ----------------------------- 
# -----------------------------------------------------------------------------------

def infinity():
    while True:
        yield

# Process datatype
@dataclass
class Process:
    ID: str
    InternalPortNo: str
    ExternalAddress: str
    NodeInfo: Node
    TaskName: str
    CommandToRunScript: str
    CommandToKillScript: str
    Status: bool
    DomainName: str

@dataclass
class Processes:
    Processes: List[Process]

PublicProcesses: Union[Processes, None] = None

# Initial defined functions 
# Exposed functions 
def SpinProcess(process: Process):
    # Starts P2PRC process 
    os.system(process.CommandToRunScript)
    
    # concats to the public exposed IP address + The Node information exposed P2PRC
    # server port. 
    ServerAddress = process.NodeInfo.IPV4 + ":" + process.NodeInfo.ServerPort

    process.ExternalAddress = P2PRCMapPort(port=process.InternalPortNo,
                                           domainname=process.DomainName,
                                           serveraddress=ServerAddress)
    process.ID = str(uuid.uuid4())
    process.Status = True

    # Save the process to memory
    AddProcessToMemory(process)
    
    # Save to disk 
    SaveProcess()

    return process

# Kill process based on the process provided
def KillProcess(process: Process): 
    os.system(process.CommandToKillScript)
    process.Status = False

    # Remove the process from memory
    PublicProcesses.Processes.remove(process)

    # Remove from disk
    SaveProcess()

    return process

# Saves the list of processes provided as a JSON file
def SaveProcess():
    global PublicProcesses 
    with open('data.json', 'w+') as f:
        json.dump(dataclasses.asdict(PublicProcesses), f, indent=4)

# Read saves processes 
def ReadSavedProcesses():
    try:
        global PublicProcesses
        with open('data.json', 'r') as file:
            data = json.load(file) 
        PublicProcesses = dacite.from_dict(Processes,data)
    except Exception as e:
        PublicProcesses = None

# Gets called when the python file is called
ReadSavedProcesses()

# List processes
def ListProcess():
    global PublicProcesses
    return PublicProcesses

# Adds the process dataclass the to
# the global variable PublicProcess.
def AddProcessToMemory(process: Process):
    global PublicProcesses
    if PublicProcesses == None:
        PublicProcesses = Processes(Processes=[process])
        # PublicProcesses.Processes.append(process)
    else: 
        PublicProcesses.Processes.append(process)

# Tracks processes in the background and removes them
# if not able to ping to the process
def BackgroundTrackProcess():
    global PublicProcesses 
    while 1:
        print("starting background process")
        for i in PublicProcesses.Processes:
            if not check_ping(i.ExternalAddress):
                i.Status = False
                SaveProcess()
            time.sleep(3)


def check_ping(host):
    try:
        page = requests.get('http://' + host)
        if page.status_code == 200:
            return True
        return False
    except:
        return False
    



# source: https://stackoverflow.com/questions/26468640/python-function-to-test-ping
# def check_ping(host: str):
#     response = os.system("ping -c 1 " + host)
#     if response == 0:
#         pingstatus = True
#     else:
#         pingstatus = False
#     return pingstatus




    


   
    

# def ProcessInformation():

# def ListProcess():
    


 