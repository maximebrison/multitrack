"""
Multitrack library.
"""
from multitrack.UDPListener import UDPListener
from multitrack.models import PluginInfo
from multitrack.MultitrackBridge import MultitrackBridge
from fastapi import FastAPI
from configparser import ConfigParser
import uvicorn
import asyncio
import logging
import signal

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s - %(name)s: %(message)s")

class MultitrackPlugin():
    def __init__(self, http_port: int, discovery_port: int, discovery_msg: str, bridge: MultitrackBridge):
        # Initialize FastAPI
        self.http_port = http_port
        self.app = FastAPI()
        self._init_routes()
        # Initialize MultitrackBridge
        self.bridge = bridge
        # Misc. props
        self.discovery_port = discovery_port
        self.discovery_msg = discovery_msg

    def run(self):
        self.info = PluginInfo(
            id = self._get_id(),
            port = self.http_port,
            actions = self.bridge.available_actions(),
            text = self.bridge.supports_text()
        )
        asyncio.run(self._main())

    def _init_routes(self):
        @self.app.get("/")
        def home():
            return "up"

        @self.app.get("/action")
        def action(action: str, target: str):
            return self.bridge.execute(action, target)

        @self.app.get("/text")
        def text(target: str, text: str):
            if not self.bridge.send_text != None:
                return "Sending text messages not supported."
            self.bridge.send_text(target, text)

    def _get_id(self):
        config = ConfigParser()
        config.read("config.ini")
        #return config["API"]["id"]
        return "default"

    async def _main(self):
        # Handle gracefull shutdown on SIGINT and SIGTERM
        stop = asyncio.Event()
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop.set)
        # Run async tasks
        await asyncio.gather(
            self._run_discovery_listener(stop),
            self._run_http_server(),
            self.bridge.run(stop)
        )

    async def _run_http_server(self):
        config = uvicorn.Config(self.app, host="0.0.0.0", port=self.http_port)
        server = uvicorn.Server(config)
        await server.serve()

    async def _run_discovery_listener(self, stop: asyncio.Event):
        self.udp_listener = UDPListener(
            self.discovery_port, 
            self.discovery_msg,
            self.info
        )

        await self.udp_listener.run(stop)