from pydantic import BaseModel

class PluginInfo(BaseModel):
    id: str
    port: int
    actions: list[str]