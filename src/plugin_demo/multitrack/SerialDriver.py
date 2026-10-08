from typing import Callable, Literal, get_type_hints
from pydantic import BaseModel
from serial import Serial
from .models import CoreAction, Action
import logging
import inspect

log = logging.getLogger("SerialDriver")

class SerialDriver():
    """
    Abstract class that serves as a template for **Serial communication**.\n
    Here's how you write your driver :
    - Create a new class **inheriting** from this one
    - Overwrite the **demux()** method with your own
    - Provide a **Serial object** and specific **bol/eol** when initializing the class
    - Bind specific **actions** using the **@driver.action()** decorator
    - Bind it to the **SerialBridge**
    """
    def __init__(self, serial: Serial, bol: bytes, eol: bytes, MSGCH: int = -1, DEFCH: int = -1, verbose: bool = False):
        # Misc. properties
        self.verbose = verbose
        # Serial obj. and properties
        self.serial = serial
        self.bol = bol
        self.eol = eol
        self.MSGCH = MSGCH
        self.DEFCH = DEFCH
        # Radio comm. handlers
        self.actions: dict[str, Action] = {}

    def send_command(self, cmd: str):
        """
        Gets a raw **str** command and sends it to the Serial port.
        """
        try:
            self.serial.write(self.bol + cmd.encode("utf-8") + self.eol)
        except Exception as e:
            log.error(f"Couldn't send {cmd}: {e}")

    def receive_command(self):
        """
        Reads raw **bytes** command from the Serial port, then sends them to the **demux()**
        """
        self.demux("sample")
    
    def demux(self, cmd: str):
        """
        Place here every **command** your radio may receive.\n
        Returns sanitized output for the *Core*
        """
        pass

    # Decorators definitions
    def action(
        self, 
        label: str,
        scope: Literal["local", "remote"] = "remote",
        method: Literal["GET", "POST"] = "POST"
    ):
        """
        @Decorator to bind actions to serial commands.\n
        **Params:**
        ```
        label: str # unique name of the action
        scope: Literal["local", "remote"] # whether the action is destined to the local radio (e.g. set_channel) or a remote (e.g. get_position)
        method: Literal["GET", "POST"] # defines the HTTP method to which the API binds the action
        ```
        **Example:**
        ```
        @driver.action(label="stun")
        def stun(payload: BaseActionModel):
            return f"*SET,IDAS,TXSTUN,IND,{payload.target}"
        ```
        """
        def action(func: Callable):
            def nfunc(payload: type[BaseModel] | None = None):
                if self.verbose: log.info(f"Executed {func(payload)}")
                if payload: return func(payload)
                return func()
            try:
                hints = get_type_hints(func)
                param = next(iter(inspect.signature(func).parameters))
                payload_type = hints[param]
            except StopIteration as e:
                payload_type = None
            self.actions[label] = Action(
                handler=nfunc,
                model=payload_type,
                scope=scope,
                method=method
            )
            print(f"{label} bound.")
            print(f"Model: {payload_type}")
            return nfunc
        return action

    def available_actions(self):
        actions: list[str]= []
        for label, action in self.actions.items():
            if action.model:
                actions.append(CoreAction(
                    label=label,
                    model=action.model.model_json_schema(),
                    scope=action.scope
                ).model_dump_json())
            else: 
                actions.append(CoreAction(
                    label=label,
                    model=action.model,
                    scope=action.scope
                ).model_dump_json())
        return actions