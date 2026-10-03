import asyncio
import json
from multitrack.models import PluginInfo

class UDPListener():
    def __init__(self, discovery_port: int, discovery_msg: str, plugin_info: PluginInfo):
        self.discovery_port = discovery_port
        self.discovery_msg = discovery_msg
        self.plugin_info = plugin_info

    async def run(self):
        loop = asyncio.get_running_loop()
        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: _DiscoveryProtocol(self.discovery_msg, self.plugin_info),
            local_addr=("0.0.0.0", self.discovery_port)
        )
        try:
            await asyncio.Future()
        finally:
            self.transport.close()

    def stop(self):
        self.transport.close()

class _DiscoveryProtocol(asyncio.DatagramProtocol):
    def __init__(self, discovery_msg: str, plugin_info: PluginInfo):
        self.discovery_msg = discovery_msg
        self.plugin_info = plugin_info

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        print("No longer listening for Discovery")

    def datagram_received(self, data, addr):
        if data != self.discovery_msg.encode():
            return

        reply = json.dumps(self.plugin_info).encode()
        self.transport.sendto(reply, addr)
        print(f"Discovery request from {addr}, replied.")