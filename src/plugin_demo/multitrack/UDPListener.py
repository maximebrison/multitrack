from .models import PluginInfo
import asyncio
import logging
import struct
import socket

log = logging.getLogger("UDPListener")

class UDPListener():
    def __init__(self, discovery_port: int, discovery_msg: str, plugin_info: PluginInfo, multicast_group: str, listening_interface: str):
        self.discovery_port = discovery_port
        self.discovery_msg = discovery_msg
        self.multicast_group = multicast_group
        self.listening_interface = listening_interface
        self.plugin_info = plugin_info
        self.transport = None

    async def start(self):
        # Get the Asyncio running loop
        loop = asyncio.get_running_loop()
        # Creates the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if hasattr(socket, "SO_REUSEPORT"):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.bind(("", self.discovery_port))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, struct.pack("4s4s", socket.inet_aton(self.multicast_group), socket.inet_aton(self.listening_interface)))
            sock.setblocking(False)
            # Opens the socket for transport, and listens asynchronously
            self.transport, _ = await loop.create_datagram_endpoint(
                lambda: _DiscoveryProtocol(self.discovery_msg, self.plugin_info),
                sock=sock
            )
        except OSError as e:
            log.error(f"Error while binding socket: {e}")
            sock.close()
            raise e

    def stop(self):
        if self.transport:
            self.transport.close()
            self.transport = None

class _DiscoveryProtocol(asyncio.DatagramProtocol):
    def __init__(self, discovery_msg: str, plugin_info: PluginInfo):
        self.discovery_msg = discovery_msg
        self.plugin_info = plugin_info

    def connection_made(self, transport):
        log.info("Listening for Discovery")
        self.transport = transport

    def connection_lost(self, exc):
        log.info("No longer listening for Discovery")

    def datagram_received(self, data, addr):
        log.info(f"received {str(data)}")
        if data != self.discovery_msg.encode():
            return

        reply = self.plugin_info.model_dump_json(indent=4).encode()
        self.transport.sendto(reply, addr)
        log.info(f"Discovery request from {addr}, replied.")