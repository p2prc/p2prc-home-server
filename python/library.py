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

p2prc = ctypes.CDLL("SharedObjects/p2prc.so")

p2prc.Init("")

# Global variable 
# A global variable will be populated on runtime.
# It is read from P2PRC directly or from a local
# database. 

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
    for _ in iter(int, 1):
        pass

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

# Initial defined functions 
# Exposed functions 
def SpinProcess(process: Process):
    # Starts P2PRC process 
    os.system(process.CommandToRunScript)

    process.ExternalAddress = P2PRCMapPort(port=process.InternalPortNo,domainname=process.DomainName,serveraddress=process.NodeInfo.ip_address.IPV4 + ":" + process.NodeInfo.ip_address.ServerPort)
    process.ID = str(uuid.uuid4())
    process.Status = True
    return process

# Kill process based on the process provided
def KillProcess(process: Process): 
    os.system(process.CommandToKillScript)
    process.Status = False
    return process
    

# def ProcessInformation():

# def ListProcess():
    


 