from pydantic import BaseModel
from typing import Literal, Callable, Any

class Action(BaseModel):
    handler: Callable[[type[BaseModel] | None], str]
    model: type[BaseModel] | None
    scope: Literal["local", "remote"]
    method: Literal["GET", "POST"]

class CoreAction(BaseModel):
    label: str
    model: dict[str, Any] | None
    scope: Literal["local", "remote"]

class PluginInfo(BaseModel):
    id: str
    port: int
    actions: list[str]

class BaseActionModel(BaseModel):
    target: str

class BaseTextModel(BaseModel):
    target: str
    msg: str

class ChannelModel(BaseModel):
    channel: str