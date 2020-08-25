# Inspired by the work of https://github.com/bremor/bonaire_myclimate,  https://github.com/bremor/bonaire_myclimate/blob/master/custom_components/bonaire_myclimate/BonairePyClimate/bonairepyclimate.py

import asyncio
import datetime
import socket
import xml.etree.ElementTree

DELETE = "<myclimate><delete>connection</delete></myclimate>"
DISCOVERY = "<myclimate><get>discovery</get><ip>{}</ip><platform>android</platform><version>1.0.0</version></myclimate>"
GETZONEINFO = "<myclimate><get>getzoneinfo</get><zoneList>1,2</zoneList></myclimate>"
INSTALLATION = "<myclimate><get>installation</get></myclimate>"
LOCAL_PORT = 10003
PROVISION = "<myclimate><post>provision</post><ssid>{}</ssid><password>{}</password><user>...</user><key>1234567890</key></myclimate>"
UDP_DISCOVERY_PORT = 10001

class HandleUDPBroadcast:
    def __init__(self, message):
        self.message = message

    def connection_made(self, transport):
        print("Sending discovery")
        sock = transport.get_extra_info("socket")
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        transport.sendto(self.message.encode())
        transport.close()

    def connection_lost(self, exc):
        pass

class HandleServer(asyncio.Protocol):
    def __init__(self, parent):
        self._parent = parent
        self._transport = None

    def connection_made(self, transport):
        print("Connected to Wifi Module")
        self._parent._server_transport = transport
        self._transport = transport
        dat = INSTALLATION.encode()
        print("Data being sent: {}".format(dat))
        transport.write(dat)

        dat = PROVISION.format(self._parent._wifi_ssid, self._parent._wifi_pword).encode()
        print("Data being sent: {}".format(dat))
        transport.write(dat)

    def data_received(self, data):
        message = data.decode()
        print("Server data received: {}".format(message))
        root = xml.etree.ElementTree.fromstring(message)

        # Expected Response:
        # <myclimate><response>provision</provision><user>...</user><status>1</status></myclimate>

        # Check if the message is a discovery response
        if root.find('response') is not None and root.find('response').text == 'discovery':
            self._parent._connected = True

        provision = root.find('response') is not None and root.find('response').text == 'provision'
        

    def connection_lost(self, exc):
        print("Server connection lost")
        self._parent._connected = False

class BonairePyClimate():

    def __init__(self, event_loop, local_ip, ssid, pword):
        self._connected = False
        self._event_loop = event_loop
        self._local_ip = local_ip
        self._server_socket = None
        self._server_transport = None
        self._update_callback = None
        self._wifi_ssid = ssid
        self._wifi_pword = pword

        self._event_loop.create_task(self.start())

    async def start(self):

        self._server_socket = await self._event_loop.create_server(
            lambda: HandleServer(self),
            self._local_ip, LOCAL_PORT)

        while True:

            attempts = 0

            while not self._connected:

                cooloff_timer = 0 if attempts < 3 else 60 if attempts < 6 else 300
                if attempts > 0: print("Discovery failed, retrying in {}s".format(cooloff_timer + 5))
                attempts += 1
                await asyncio.sleep(cooloff_timer)

                # Send the UDP discovery broadcast
                transport, protocol = await self._event_loop.create_datagram_endpoint(
                    lambda: HandleUDPBroadcast(DISCOVERY.format(self._local_ip)),
                    remote_addr=('255.255.255.255', UDP_DISCOVERY_PORT),
                    allow_broadcast=True)

                # Wait for 7 seconds for a response to the discovery broadcast
                await asyncio.sleep(7)

            await asyncio.sleep(220)

            self._connected = False
            self._server_transport.write(DELETE.encode())

            await asyncio.sleep(3)

    def register_update_callback(self, method):
        """Public method to add a callback subscriber."""
        self._update_callback = method
