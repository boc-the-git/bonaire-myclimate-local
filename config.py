import asyncio
import socket
import time

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

async def startIt(ssid, pword):
    climate = BonairePyClimate(loop, get_ip(), ssid, pword)
    await asyncio.sleep(1800)
    return climate

print("Local machine IP: " + get_ip())

ssid = input("Enter your wifi SSID: ")
pword = input("Enter your wifi password: ")
print(ssid)
print(pword)

loop = asyncio.new_event_loop()

loop.run_until_complete(startIt(ssid, pword))

loop.close()
