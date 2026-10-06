import asyncio
import json
import logging
from multitrack.models import PluginInfo

log = logging.getLogger("UDPListener")

class UDPListener():
    def __init__(self, discovery_port: int, discovery_msg: str, plugin_info: PluginInfo):
        self.discovery_port = discovery_port
        self.discovery_msg = discovery_msg
        self.plugin_info = plugin_info

    async def run(self, stop: asyncio.Event):
        loop = asyncio.get_running_loop()
        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: _DiscoveryProtocol(self.discovery_msg, self.plugin_info),
            local_addr=("0.0.0.0", self.discovery_port)
        )
        try:
            await stop.wait()
        finally:
            self.transport.close()

    def stop(self):
        self.transport.close()

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
        if data != self.discovery_msg.encode():
            return

        reply = json.dumps(self.plugin_info.model_dump()).encode()
        self.transport.sendto(reply, addr)
        log.info(f"Discovery request from {addr}, replied.")