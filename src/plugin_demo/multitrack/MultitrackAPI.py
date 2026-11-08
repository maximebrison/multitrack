from .UDPListener import UDPListener
from .models import PluginInfo, MultitrackConfig, AdoptModel
from .Elements import RemoteElements, LocalElements
from .SerialBridge import SerialBridge
from .SerialDriver import SerialDriver
from fastapi import FastAPI, APIRouter, Response
from contextlib import asynccontextmanager
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed
import uvicorn
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(asctime)s - %(name)s: %(message)s")
log = logging.getLogger("MultitrackAPI")

class MultitrackAPI():
    """
    Manages the communication between your plugin and the **Multitrack Core**\n
    Exposes the *API endpoints*, runs the *UDPBroadcast listener*, connects to the Core's *WebSocket Server*, manages *plugin configuration*... 
    """
    def __init__(self, http_port: int, discovery_port: int, discovery_msg: str, driver: SerialDriver, multicast_group = "239.255.42.69", listening_interface = "0.0.0.0", config_file = "F:/developpement/python/multitrack/plugin_demo/config.ini"):
        # Misc. props
        self.http_port = http_port
        self.discovery_port = discovery_port
        self.discovery_msg = discovery_msg
        self.multicast_group = multicast_group
        self.listening_interface = listening_interface
        # Websocket
        self.ws_task: asyncio.Task | None = None
        # Config
        self.config = MultitrackConfig.read(config_file)
        # Initialize MultitrackBridge
        self.bridge = SerialBridge(driver)
        # UIElements
        self.local = LocalElements()
        self.remote = RemoteElements()

        # Other inits
        self.bridge.driver.set_plugin_id(self.config.api.id)

    def run(self):
        log.info("Running application.")
        # Gather plugin info
        self.info = PluginInfo(
            id = self.config.api.id,
            port = self.http_port,
            elements = self.remote.list_elements() + self.local.list_elements(),
            bound = self.config.api.bound
        )

        # Initialize UDPListener
        self.udp_listener = UDPListener(
            self.discovery_port, 
            self.discovery_msg,
            self.info,
            self.multicast_group,
            self.listening_interface
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
        try:
            uvicorn.run(self.app, host="0.0.0.0", port=self.http_port)
        except OSError:
            print("error")

    async def _on_startup(self):
        # Runs the SerialBridge thread
        self.bridge.bind_loop(asyncio.get_running_loop())
        self.bridge.thread.start()
        for action in self.bridge.driver.on_startup():
            await self.bridge.send_command(action)
        # Runs UDP Listener
        await self.udp_listener.start()
        # Runs the WebSocket connection with the Core
        if self.config.api.bound:
            try:
                self.ws_task = asyncio.create_task(self._connect_to_core())
            except ConnectionError as e:
                log.error(e)

    async def _on_shutdown(self):
        # Stops SerialBridge thread
        self.bridge.stop_sig.set()
        await asyncio.to_thread(self.bridge.thread.join)
        # Stops UDP Listener
        self.udp_listener.stop()
        # Stops the WebSocket connection
        if self.ws_task:
            self.ws_task.cancel()
            log.info("Disconnected from the Core")

    async def _connect_to_core(self):
        if not self.config.api.token: raise ConnectionError("API Token not loaded")
        async for ws in connect(f"ws://{self.config.api.core_host}/plugins?id={self.config.api.id}", additional_headers={"bearer-token": self.config.api.token}):
            try:
                log.info(f"Connected to Core on {self.config.api.core_host}")
                self.ws = ws
                async for data in self._fetch_cmds_from_bridge():
                    await ws.send(data)
            except ConnectionClosed:
                continue

    async def _fetch_cmds_from_bridge(self):
        try:
            while True:
                yield await self.bridge.events.get()
        except:
            pass

    def _init_routes(self):
        @self.app.get("/")
        async def home():
            return self.info

        @self.app.get("/restart")
        async def restart():
            raise KeyboardInterrupt

        @self.app.post("/adopt")
        async def adopt(payload: AdoptModel):
            if(self.config.api.bound): return Response(status_code=403, content="Plugin already bound.")

            self.config.api.core_host = payload.host
            self.config.api.token = payload.token
            self.config.api.bound = True
            self.config.write()

            self.ws_task = asyncio.create_task(self._connect_to_core())

            return Response(status_code=200, content="Successfully bound plugin.")

        remote_router = APIRouter(
            prefix="/remote"
        )

        local_router = APIRouter(
            prefix="/local"
        )

        for (path, element) in self.remote.elements.items():
            remote_router.add_api_route(
                path=f"/{path}",
                endpoint=element.make_endpoint(self.bridge.send_command),
                methods=[element.metadata.method],
                name=path
            )

        for (path, element) in self.local.elements.items():
            local_router.add_api_route(
                path=f"/{path}",
                endpoint=element.make_endpoint(self.bridge.send_command),
                methods=[element.metadata.method],
                name=path
            )

        self.app.include_router(remote_router)
        self.app.include_router(local_router)