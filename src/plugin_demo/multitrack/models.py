from pydantic import BaseModel
from typing import Literal, Callable, Any
from types import CoroutineType
from configparser import ConfigParser
from uuid import uuid4

# Metadata

class GeneralMetadata(BaseModel):
    path: str
    element: Literal["button", "text", "number", "chatbox", "toggle", "dropdown"]
    blocking: bool
    scope: Literal["local", "remote"] = "remote"
    role: Literal["operator", "admin"] = "operator"
    method: Literal["GET", "POST"] = "POST"
    group: str | None = None
    sensible: bool = False
    display_text: str | None = None
    tooltip: str | None = None

class ToggleMetadata(GeneralMetadata):
    ref: str
    colors: tuple[str, str] | None = None

class ChatboxMetadata(GeneralMetadata):
    ref: str

class NumberMetadata(GeneralMetadata):
    ref: str
    vartype: Literal["int", "float"]
    min_max: tuple[int | float, int | float] | None = None

class DropdownMetadata(GeneralMetadata):
    ref: str
    values: list[str]

class Element(BaseModel):
    handler: Callable[..., str]
    check_ack: Callable[[str], bool] | None = None
    metadata: GeneralMetadata | type[GeneralMetadata]

    def make_endpoint(self, send_command: Callable[[str, Callable[[str], bool] | None], CoroutineType[Any, Any, None]]):
        if self.metadata.scope == "remote":
            match self.metadata.element:
                case "button":
                    async def remote_button(e: EntityInfo):
                        await send_command(self.handler(e), self.check_ack)
                    return remote_button
                case "chatbox":
                    async def remote_chatbox(e: EntityInfo, msg: str):
                        await send_command(self.handler(e, msg), self.check_ack)
                    return remote_chatbox
                case "dropdown":
                    async def remote_dropdown(e: EntityInfo, value: str):
                        await send_command(self.handler(e, value), self.check_ack)
                    return remote_dropdown
                case "number":
                    async def remote_number(e: EntityInfo, value: int | float):
                        await send_command(self.handler(e, value), self.check_ack)
                    return remote_number
                case "text":
                    async def remote_text(e: EntityInfo, msg: str):
                        await send_command(self.handler(e, msg), self.check_ack)
                    return remote_text
                case "toggle":
                    async def remote_toggle(e: EntityInfo, state: bool):
                        await send_command(self.handler(e, state), self.check_ack)
                    return remote_toggle
        else:
            match self.metadata.element:
                case "button":
                    async def local_button():
                        await send_command(self.handler(), self.check_ack)
                    return local_button
                case "chatbox":
                    async def local_chatbox(msg: str):
                        await send_command(self.handler(msg), self.check_ack)
                    return local_chatbox
                case "dropdown":
                    async def local_dropdown(value: str):
                        await send_command(self.handler(value), self.check_ack)
                    return local_dropdown
                case "number":
                    async def local_number(value: int | float):
                        await send_command(self.handler(value), self.check_ack)
                    return local_number
                case "text":
                    async def local_text(msg: str):
                        await send_command(self.handler(msg), self.check_ack)
                    return local_text
                case "toggle":
                    async def local_toggle(state: bool):
                        await send_command(self.handler(state), self.check_ack)
                    return local_toggle

# Infos

class EntityInfo(BaseModel):
    serial: int

class PluginInfo(BaseModel):
    id: str
    port: int
    elements: list[GeneralMetadata | type[GeneralMetadata]]
    bound: bool

# Data

class TextMessage(BaseModel):
    msg: str

class GPSPosition(BaseModel):
    latitude: float
    longitude: float

class StatusUpdate(BaseModel):
    status: str

class CoreData(BaseModel):
    plugin_id: str
    entity_id: str | None
    timestamp: float
    type: Literal["text", "gps", "status", "err"]
    success: bool
    data: TextMessage | GPSPosition | StatusUpdate | None

class AdoptModel(BaseModel):
    host: str
    token: str

class APIConfig(BaseModel):
    id: str
    core_host: str | None
    token: str | None
    bound: bool

class MultitrackConfig(BaseModel):
    filepath: str
    api: APIConfig

    @classmethod
    def read(cls, filepath: str):
        config = ConfigParser()
        config.read(filepath)
        try:
            api = APIConfig(
                id = config["API"]["id"],
                core_host = None if config["API"]["core_host"] == "None" else config["API"]["core_host"],
                token = None if config["API"]["token"] == "None" else config["API"]["token"],
                bound = config["API"]["bound"] == "True"
            )
            print("Config loaded.")
            return cls(
                filepath = filepath,
                api = api
            )
        except:
            print("Couldn't parse config, generating defaults.")
            config = cls.default(filepath)
            config.write()
            return config

    @classmethod
    def default(cls, filepath: str):
        return cls(
            filepath = filepath,
            api = APIConfig(
                id = str(uuid4()),
                core_host = None,
                token = None,
                bound = False
            )
        )

    def write(self):
        config = ConfigParser()
        config["API"] = {}
        config["API"]["id"] = self.api.id
        config["API"]["core_host"] = str(self.api.core_host)
        config["API"]["token"] = str(self.api.token)
        config["API"]["bound"] = str(self.api.bound)

        with open(self.filepath, "w") as f:
            config.write(f)