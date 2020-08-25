import sys
import asyncio
import socket
#import time

from bonaire_local import BonairePyClimate

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def update_callback(self):
        """Call update method."""
        print("Do I need to do anything here..?")

async def startIt(IP, ssid, pword):
    #asyncio.wait(BonairePyClimate(loop, IP, ssid, pword))
    climate = BonairePyClimate(loop, IP, ssid, pword)
    await asyncio.sleep(300)
    return climate

IP = get_ip()
print("Local machine IP: " + IP)

ssid = input("Enter your wifi SSID: ")
pword = input("Enter your wifi password: ")
print("")
print("=======")
print("SSID: "+ssid)
print("Password: "+pword)
print("=======")
print("")

yorn = input("Please confirm you wish to proceed with the above details? [y/N] ")
if yorn.upper() != "Y":
   sys.exit()

loop = asyncio.new_event_loop()

loop.run_until_complete(startIt(IP, ssid, pword))

loop.close()
