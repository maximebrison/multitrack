from pydantic import BaseModel
from typing import Literal

class State(BaseModel):
    scope: Literal["local", "remote"]
    label: str
    type: Literal["str", "int", "float", "bool"]

class StateStore():
    def __init__(self):
        pass