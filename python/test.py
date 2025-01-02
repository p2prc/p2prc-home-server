from library import *


if __name__ == "__main__":
    P2PRCNodes = ListNodes()

    # Create sample process 
    sample_process = Process(
       ID="",
       TaskName="TestServer",
       InternalPortNo="8084",
       NodeInfo=IPAddress(P2PRCNodes.ip_address[2]),
       CommandToRunScript="sh SamplePythonTestServer/server.sh &",
       CommandToKillScript="sh SamplePythonTestServer/killserver.sh",
       DomainName="",
       Status=False,
       ExternalAddress=""
    )

    print("------------ Starting process -------------")

    # Spin process
    sample_process = SpinProcess(sample_process)

    print("------------ Process Public address -------------")
    
    # Prints status of the current process 
    print(sample_process.ExternalAddress)

    print("------------ Process kept waiting for 20 seconds -------------")

    # Runs the process for 20 seconds
    time.sleep(20)

    print("------------ Process getting killed -------------")

    # Kills the process 
    KillProcess(sample_process)

    print("------------ Process current process -------------")

    # Prints process status 
    print(sample_process.Status)