"""
Multitrack library.
"""
from multitrack.UDPListener import UDPListener
from fastapi import FastAPI
import uvicorn
from collections.abc import Callable
import asyncio

class MultitrackPlugin():
    def __init__(self, http_port: int, discovery_port: int, discovery_msg: str):
        # Initialize FastAPI
        self.http_port = http_port
        self.app = FastAPI()
        self.init_routes()
        # Initialize props
        self.discovery_port = discovery_port
        self.discovery_msg = discovery_msg
        self.actions: dict[str, Callable[[], None]] = {}

    def run(self):
        asyncio.run(self.main())

    async def main(self):
        await asyncio.gather(
            self.run_discovery_listener(),
            self.run_http_server()
        )

    async def run_http_server(self):
        config = uvicorn.Config(self.app, host="0.0.0.0", port=self.http_port)
        server = uvicorn.Server(config)
        await server.serve()

    async def run_discovery_listener(self):
        self.udp_listener = UDPListener(
            self.discovery_port, 
            self.discovery_msg,
            {
                "id": "Test",
                "port": self.http_port,
                "actions": []
            }
        )

        await self.udp_listener.run()

    def init_routes(self):
        @self.app.get("/")
        def home():
            return "up"

        @self.app.get("/action")
        def action(action: str):
            return action

    def bind_action(self, action: str, handler: Callable):
        self.actions[action] = handler