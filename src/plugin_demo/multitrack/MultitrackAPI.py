from .UDPListener import UDPListener
from .models import PluginInfo, Action
from .SerialBridge import SerialBridge
from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s - %(name)s: %(message)s")

class MultitrackAPI():
    """
    Manages the communication between your plugin and the **Multitrack Core**\n
    Exposes the *API endpoints*, runs the *UDPBroadcast listener*, manages *plugin configuration*... 
    """
    def __init__(self, http_port: int, discovery_port: int, discovery_msg: str, bridge: SerialBridge):
        # Misc. props
        self.discovery_port = discovery_port
        self.discovery_msg = discovery_msg
        self.http_port = http_port
        # Initialize MultitrackBridge
        self.bridge = bridge

    def run(self):
        # Gather plugin info
        self.info = self._gather_info()

        # Initialize UDPListener
        self.udp_listener = UDPListener(
            self.discovery_port, 
            self.discovery_msg,
            self.info
        )

        # Initialize lifespan events (on_startup/on_shutdown)
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await self._on_startup()
            yield
            await self._on_shutdown()

        # Initialize FastAPI
        self.app = FastAPI(lifespan=lifespan)
        self._init_routes()

        # Runs FastAPI (with lifespan handlers)
        uvicorn.run(self.app, host="0.0.0.0", port=self.http_port)

    async def _on_startup(self):
        # Runs the SerialBridge thread
        self.bridge.bind_loop(asyncio.get_running_loop())
        self.bridge.thread.start()
        # Runs UDP Listener
        await self.udp_listener.run()

    async def _on_shutdown(self):
        # Stops SerialBridge thread
        self.bridge.stop_sig.set()
        await asyncio.to_thread(self.bridge.thread.join)
        # Stops UDP Listener
        self.udp_listener.stop()

    def _init_routes(self):
        @self.app.get("/")
        async def home():
            return "up"

        action_router = APIRouter(
            prefix="/action"
        )

        for (label, action) in self.bridge.driver.actions.items():
            action_router.add_api_route(
                path=f"/{label}",
                endpoint=self._make_endpoint(action),
                methods=[action.method],
                name=label
            )

        self.app.include_router(action_router)

    def _make_endpoint(self, action: Action):
        if not action.model == None:
            async def endpoint(payload):
                await self.bridge.send_command(action.handler(payload))
            endpoint.__annotations__["payload"] = action.model
            return endpoint
        else:
            async def endpoint_no_payload():
                await self.bridge.send_command(action.handler(None))
            return endpoint_no_payload

    def _gather_info(self):
        return PluginInfo(
            id = "default",
            port = self.http_port,
            actions = self.bridge.driver.available_actions()
        )