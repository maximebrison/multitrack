import logging
from typing import Callable, Literal, Any
from .models import Element, EntityInfo, GeneralMetadata, ToggleMetadata, ChatboxMetadata, NumberMetadata, DropdownMetadata

log = logging.getLogger("MultitrackAPI")

class RemoteElements():
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.elements: dict[str, Element] = {}

    def list_elements(self):
        elements: list[GeneralMetadata | type[GeneralMetadata]]= []
        for e in self.elements.values():
            elements.append(e.metadata)
        return elements
    
    # Decorators definitions
    def button(
        self,
        path: str,
        check_ack: Callable[[str], bool] | None = None,
        role: Literal["operator", "admin"] = "operator",
        method: Literal["GET", "POST"] = "POST",
        group: str | None = None,
        sensible: bool = False,
        display_text: str | None = None,
        tooltip: str | None = None        
    ):
        """
        Creates a button to execute serial commands.\n
        ### Params
        path: Name of the endpoint. Will then be accessible through `/action/{path}`. [REQUIRED].\n
        role: Determine which role has access to this route.\n
        method: Define the HTTP method to which the API binds the action.\n
        check_ack: If specified, the SerialBridge will queue every other outgoing commands until the condition is fullfilled. Takes the read line as param.\n
        group: Specify the UI group to which the action belongs.\n
        sensible: Specify whether the action needs confirmation before executing.\n
        display_text: Name to display on the UI. If None, capitalize the *label* and replace every "_" with whitespaces.\n
        tooltip: Specify the on_hover tooltip.\n
        ### Decorated params
        e: Snapshot of the targetted EntityInfo from the Core at request time.\n
        ### Decorated return
        Your Serial command (as a *string*) for the specific *action*.
        ### Example
        ```
        @app.remote.button(
            path = "get_position",
            check_ack = lambda x: "ACK,OK" in x or "ACK,NG" in x,
            group = "Basic actions",
            tooltip = "Ask for the position of the remote entity"
            )
        def get_position(e: EntityInfo):
            return f'*SET,IDAS,TXSTAT,IND,{e.serial},{driver.local_id},24'
        ```
        """
        def button(func: Callable[[EntityInfo], str]):
            def nfunc(e: EntityInfo):
                if self.verbose: log.info(f"Executed {func(e)}")
                return func(e)
            self.elements[path] = Element(
                handler = nfunc,
                check_ack = check_ack,
                metadata = GeneralMetadata(
                    path=path,
                    element="button",
                    blocking=check_ack != None,
                    scope="remote",
                    role=role,
                    method=method,
                    group=group,
                    sensible=sensible,
                    display_text=display_text if display_text else path.replace("_", " ").capitalize(),
                    tooltip=tooltip
                )
            )
            if self.verbose: log.info(f"{path} bound.")
            return nfunc
        return button
    
    def toggle(
        self,
        path: str,
        ref: str,
        check_ack: Callable[[str], bool] | None = None,
        role: Literal["operator", "admin"] = "operator",
        method: Literal["GET", "POST"] = "POST",
        group: str | None = None,
        sensible: bool = False,
        display_text: str | None = None,
        tooltip: str | None = None,
        colors: tuple[str, str] | None = None
    ):
        """
        Creates a toggle button to execute serial commands.\n
        ### Params
        path: Name of the endpoint. Will then be accessible through `/action/{path}`. [REQUIRED].\n
        ref: Value bound to the toggle's state. Check full documentation for more info. [REQUIRED]\n
        role: Determine which role has access to this route.\n
        method: Define the HTTP method to which the API binds the action.\n
        check_ack: If specified, the SerialBridge will queue every other outgoing commands until the condition is fullfilled. Takes the read line as param.\n
        group: Specify the UI group to which the action belongs.\n
        sensible: Specify whether the action needs confirmation before executing.\n
        display_text: Name to display on the UI. If None, capitalize the *label* and replace every "_" with whitespaces.\n
        tooltip: Specify the on_hover tooltip.\n
        colors: HEX values for the button's off/on colors respectively. If None, the Core will default to red/green.\n
        ### Decorated params
        e: Snapshot of the targetted EntityInfo from the Core at request time.\n
        state: State of the *ref* from the Core at request time.\n
        ### Decorated return
        Your Serial command (as a *string*) for the specific *action*.
        ### Example
        ```
        @app.remote.toggle(
            path = "stun",
            ref = "is_stun",
            check_ack = lambda x: "ACK,OK" in x or "ACK,NG" in x,
            group = "Basic actions",
            tooltip = "Toggle the STUN status of a radio."
            )
        def toggle_stun(e: EntityInfo, state: bool):
            if state:
                return f'*SET,IDAS,TXREVIVE,IND,{e.serial},{driver.local_id}'
            else:
                return f'*SET,IDAS,TXSTUN,IND,{e.serial},{driver.local_id}'
        ```
        """
        def toggle(func: Callable[[EntityInfo, bool], str]):
            def nfunc(e: EntityInfo, state: bool):
                if self.verbose: log.info(f"Executed {func(e, state)}")
                return func(e, state)
            self.elements[path] = Element(
                handler = nfunc,
                check_ack = check_ack,
                metadata = ToggleMetadata(
                    path=path,
                    element="toggle",
                    blocking=check_ack != None,
                    scope="remote",
                    role=role,
                    method=method,
                    group=group,
                    sensible=sensible,
                    display_text=display_text if display_text else path.replace("_", " ").capitalize(),
                    tooltip=tooltip,
                    ref=ref,
                    colors=colors
                )
            )
            if self.verbose: log.info(f"{path} bound.")
            return nfunc
        return toggle
    
    def chatbox(
        self,
        path: str,
        ref: str = "general",
        check_ack: Callable[[str], bool] | None = None,
        role: Literal["operator", "admin"] = "operator",
        method: Literal["GET", "POST"] = "POST",
        group: str | None = None,
        sensible: bool = False,
        display_text: str | None = None,
        tooltip: str | None = None
    ):
        """
        Creates a chatbox (input and history) to handle text messages. You can specify a *ref* to filter where the messages come from/go to if your device supports multiple "channel-like" messaging.\n
        ### Params
        path: Name of the endpoint. Will then be accessible through `/action/{path}`. [REQUIRED].\n
        ref: Value bound to the origin/destination of the messages. Check full documentation for more info.\n
        role: Determine which role has access to this route.\n
        method: Define the HTTP method to which the API binds the action.\n
        check_ack: If specified, the SerialBridge will queue every other outgoing commands until the condition is fullfilled. Takes the read line as param.\n
        group: Specify the UI group to which the action belongs.\n
        sensible: Specify whether the action needs confirmation before executing.\n
        display_text: Name to display on the UI. If None, capitalize the *label* and replace every "_" with whitespaces.\n
        tooltip: Specify the on_hover tooltip.\n
        ### Decorated params
        e: Snapshot of the targetted EntityInfo from the Core at request time.\n
        msg: Message to send.\n
        ### Decorated return
        Your Serial command (as a *string*) for the specific *action*.
        ### Example
        ```
        @app.remote.chatbox(
            path = "send_message",
            check_ack = lambda x: "ACK,OK" in x or "ACK,NG" in x,
            tooltip = "Send a message to a remote entity"
            )
        def send_message(e: EntityInfo, msg: str):
            return f'*SET,IDAS,TXMSG,IND,{e.serial},{driver.local_id},MSG,"{msg.replace("\"", "\'")}"'
        ```
        """
        def chatbox(func: Callable[[EntityInfo, str], str]):
            def nfunc(e: EntityInfo, msg: str):
                if self.verbose: log.info(f"Executed {func(e, msg)}")
                return func(e, msg)
            self.elements[path] = Element(
                handler = nfunc,
                check_ack = check_ack,
                metadata = ChatboxMetadata(
                    path=path,
                    element="chatbox",
                    blocking=check_ack != None,
                    scope="remote",
                    role=role,
                    method=method,
                    group=group,
                    sensible=sensible,
                    display_text=display_text if display_text else path.replace("_", " ").capitalize(),
                    tooltip=tooltip,
                    ref=ref
                )
            )
            if self.verbose: log.info(f"{path} bound.")
            return nfunc
        return chatbox
    
    def text(
        self,
        path: str,
        check_ack: Callable[[str], bool] | None = None,
        role: Literal["operator", "admin"] = "operator",
        method: Literal["GET", "POST"] = "POST",
        group: str | None = None,
        sensible: bool = False,
        display_text: str | None = None,
        tooltip: str | None = None
    ):
        """
        Creates a text input to send texts to a remote entity.\n
        For managing messages with history, you'd want to use a Chatbox instead.\n
        ### Params
        path: Name of the endpoint. Will then be accessible through `/action/{path}`. [REQUIRED].\n
        role: Determine which role has access to this route.\n
        method: Define the HTTP method to which the API binds the action.\n
        check_ack: If specified, the SerialBridge will queue every other outgoing commands until the condition is fullfilled. Takes the read line as param.\n
        group: Specify the UI group to which the action belongs.\n
        sensible: Specify whether the action needs confirmation before executing.\n
        display_text: Name to display on the UI. If None, capitalize the *label* and replace every "_" with whitespaces.\n
        tooltip: Specify the on_hover tooltip.\n
        ### Decorated params
        e: Snapshot of the targetted EntityInfo from the Core at request time.\n
        msg: Message to send.\n
        ### Decorated return
        Your Serial command (as a *string*) for the specific *action*.
        ### Example
        ```
        @app.remote.text(
            path = "set_friendly_name",
            check_ack = lambda x: "ACK,OK" in x or "ACK,NG" in x,
            tooltip = "Set a remote friendly name."
            )
        def set_friendly_name(e: EntityInfo, msg: str):
            return f'*SET,IDAS,TXFNAME,IND,{e.serial},{driver.local_id},MSG,"{msg.replace("\"", "\'")}"'
        ```
        """
        def text(func: Callable[[EntityInfo, str], str]):
            def nfunc(e: EntityInfo, msg: str):
                if self.verbose: log.info(f"Executed {func(e, msg)}")
                return func(e, msg)
            self.elements[path] = Element(
                handler = nfunc,
                check_ack = check_ack,
                metadata = GeneralMetadata(
                    path=path,
                    element="text",
                    blocking=check_ack != None,
                    scope="remote",
                    role=role,
                    method=method,
                    group=group,
                    sensible=sensible,
                    display_text=display_text if display_text else path.replace("_", " ").capitalize(),
                    tooltip=tooltip,
                )
            )
            if self.verbose: log.info(f"{path} bound.")
            return nfunc
        return text
    
    def number(
        self,
        path: str,
        ref: str,
        vartype: Literal["int", "float"],
        min_max: tuple[int | float, int | float] | None = None,
        check_ack: Callable[[str], bool] | None = None,
        role: Literal["operator", "admin"] = "operator",
        method: Literal["GET", "POST"] = "POST",
        group: str | None = None,
        sensible: bool = False,
        display_text: str | None = None,
        tooltip: str | None = None
    ):
        """
        Creates a number input to send numeric values.\n
        Can be either int or float.\n
        ### Params
        path: Name of the endpoint. Will then be accessible through `/action/{path}`. [REQUIRED].\n
        ref: Value bound to the number input. Check full documentation for more info. [REQUIRED].\n
        vartype: Specify whether it's an int or a float. [REQUIRED].\n
        min_max: Minimum and maximum values (respectively) for the number input.\n
        role: Determine which role has access to this route.\n
        method: Define the HTTP method to which the API binds the action.\n
        check_ack: If specified, the SerialBridge will queue every other outgoing commands until the condition is fullfilled. Takes the read line as param.\n
        group: Specify the UI group to which the action belongs.\n
        sensible: Specify whether the action needs confirmation before executing.\n
        display_text: Name to display on the UI. If None, capitalize the *label* and replace every "_" with whitespaces.\n
        tooltip: Specify the on_hover tooltip.\n
        ### Decorated params
        e: Snapshot of the targetted EntityInfo from the Core at request time.\n
        value: Value sent.\n
        ### Decorated return
        Your Serial command (as a *string*) for the specific *action*.
        ### Example
        ```
        @app.remote.number(
            path = "set_channel",
            ref = "channel",
            vartype = "int",
            min_max = (1, 16),
            check_ack = lambda x: "ACK,OK" in x or "ACK,NG" in x,
            tooltip = "Set a remote channel."
            )
        def set_channel(e: EntityInfo, value: int | float):
            return f'*SET,IDAS,TXCH,IND,{e.serial},{driver.local_id},CH,"{value}"'
        ```
        """
        def number(func: Callable[[EntityInfo, int | float], str]):
            def nfunc(e: EntityInfo, value: int | float):
                if self.verbose: log.info(f"Executed {func(e, value)}")
                return func(e, value)
            self.elements[path] = Element(
                handler = nfunc,
                check_ack = check_ack,
                metadata = NumberMetadata(
                    path=path,
                    element="number",
                    blocking=check_ack != None,
                    scope="remote",
                    role=role,
                    method=method,
                    group=group,
                    sensible=sensible,
                    display_text=display_text if display_text else path.replace("_", " ").capitalize(),
                    tooltip=tooltip,
                    ref=ref,
                    vartype=vartype,
                    min_max=min_max
                )
            )
            if self.verbose: log.info(f"{path} bound.")
            return nfunc
        return number
    
    def dropdown(
        self,
        path: str,
        ref: str,
        values: list[str],
        check_ack: Callable[[str], bool] | None = None,
        role: Literal["operator", "admin"] = "operator",
        method: Literal["GET", "POST"] = "POST",
        group: str | None = None,
        sensible: bool = False,
        display_text: str | None = None,
        tooltip: str | None = None
    ):
        """
        Creates a dropdown that restrict the user to the specified options.\n
        ### Params
        path: Name of the endpoint. Will then be accessible through `/action/{path}`. [REQUIRED].\n
        ref: Value bound to the dropdown. Check full documentation for more info. [REQUIRED].\n
        values: List of values (str) the dropdown has. [REQUIRED].\n
        role: Determine which role has access to this route.\n
        method: Define the HTTP method to which the API binds the action.\n
        check_ack: If specified, the SerialBridge will queue every other outgoing commands until the condition is fullfilled. Takes the read line as param.\n
        group: Specify the UI group to which the action belongs.\n
        sensible: Specify whether the action needs confirmation before executing.\n
        display_text: Name to display on the UI. If None, capitalize the *label* and replace every "_" with whitespaces.\n
        tooltip: Specify the on_hover tooltip.\n
        ### Decorated params
        e: Snapshot of the targetted EntityInfo from the Core at request time.\n
        value: Value sent.\n
        ### Decorated return
        Your Serial command (as a *string*) for the specific *action*.
        ### Example
        ```
        @app.remote.dropdown(
            path = "set_channel",
            ref = "channel",
            values = ["2", "8", "24"]
            check_ack = lambda x: "ACK,OK" in x or "ACK,NG" in x,
            tooltip = "Set a remote channel."
            )
        def set_channel(e: EntityInfo, value: str):
            return f'*SET,IDAS,TXCH,IND,{e.serial},{driver.local_id},CH,"{value}"'
        ```
        """
        def dropdown(func: Callable[[EntityInfo, str], str]):
            def nfunc(e: EntityInfo, value: str):
                if self.verbose: log.info(f"Executed {func(e, value)}")
                return func(e, value)
            self.elements[path] = Element(
                handler = nfunc,
                check_ack = check_ack,
                metadata = DropdownMetadata(
                    path=path,
                    element="dropdown",
                    blocking=check_ack != None,
                    scope="remote",
                    role=role,
                    method=method,
                    group=group,
                    sensible=sensible,
                    display_text=display_text if display_text else path.replace("_", " ").capitalize(),
                    tooltip=tooltip,
                    ref=ref,
                    values=values
                )
            )
            if self.verbose: log.info(f"{path} bound.")
            return nfunc
        return dropdown

class LocalElements():
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.elements: dict[str, Element] = {}

    def list_elements(self):
        elements: list[GeneralMetadata | type[GeneralMetadata]]= []
        for e in self.elements.values():
            elements.append(e.metadata)
        return elements
    
    # Decorators definitions
    def button(
        self,
        path: str,
        check_ack: Callable[[str], bool] | None = None,
        role: Literal["operator", "admin"] = "operator",
        method: Literal["GET", "POST"] = "POST",
        group: str | None = None,
        sensible: bool = False,
        display_text: str | None = None,
        tooltip: str | None = None        
    ):
        """
        Creates a button to execute serial commands.\n
        ### Params
        path: Name of the endpoint. Will then be accessible through `/action/{path}`. [REQUIRED].\n
        role: Determine which role has access to this route.\n
        method: Define the HTTP method to which the API binds the action.\n
        check_ack: If specified, the SerialBridge will queue every other outgoing commands until the condition is fullfilled. Takes the read line as param.\n
        group: Specify the UI group to which the action belongs.\n
        sensible: Specify whether the action needs confirmation before executing.\n
        display_text: Name to display on the UI. If None, capitalize the *label* and replace every "_" with whitespaces.\n
        tooltip: Specify the on_hover tooltip.\n
        ### Decorated params
        None
        ### Decorated return
        Your Serial command (as a *string*) for the specific *action*.
        ### Example
        ```
        @app.local.button(
            path = "get_channel",
            group = "Basic actions",
            tooltip = "Ask for the channel."
            )
        def get_id():
            return '*GET,MCH,SEL'
        ```
        """
        def button(func: Callable[[], str]):
            def nfunc():
                if self.verbose: log.info(f"Executed {func()}")
                return func()
            self.elements[path] = Element(
                handler = nfunc,
                check_ack = check_ack,
                metadata = GeneralMetadata(
                    path=path,
                    element="button",
                    blocking=check_ack != None,
                    scope="local",
                    role=role,
                    method=method,
                    group=group,
                    sensible=sensible,
                    display_text=display_text if display_text else path.replace("_", " ").capitalize(),
                    tooltip=tooltip
                )
            )
            if self.verbose: log.info(f"{path} bound.")
            return nfunc
        return button
    
    def toggle(
        self,
        path: str,
        ref: str,
        check_ack: Callable[[str], bool] | None = None,
        role: Literal["operator", "admin"] = "operator",
        method: Literal["GET", "POST"] = "POST",
        group: str | None = None,
        sensible: bool = False,
        display_text: str | None = None,
        tooltip: str | None = None,
        colors: tuple[str, str] | None = None
    ):
        """
        Creates a toggle button to execute serial commands.\n
        ### Params
        path: Name of the endpoint. Will then be accessible through `/action/{path}`. [REQUIRED].\n
        ref: Value bound to the toggle's state. Check full documentation for more info. [REQUIRED]\n
        role: Determine which role has access to this route.\n
        method: Define the HTTP method to which the API binds the action.\n
        check_ack: If specified, the SerialBridge will queue every other outgoing commands until the condition is fullfilled. Takes the read line as param.\n
        group: Specify the UI group to which the action belongs.\n
        sensible: Specify whether the action needs confirmation before executing.\n
        display_text: Name to display on the UI. If None, capitalize the *label* and replace every "_" with whitespaces.\n
        tooltip: Specify the on_hover tooltip.\n
        colors: HEX values for the button's off/on colors respectively. If None, the Core will default to red/green.\n
        ### Decorated params
        state: State of the *ref* from the Core at request time.\n
        ### Decorated return
        Your Serial command (as a *string*) for the specific *action*.
        ### Example
        ```
        @app.local.toggle(
            path = "ptt",
            ref = "is_ptt_on",
            group = "Basic actions",
            tooltip = "Toggle the PTT."
            )
        def toggle_ptt(state: bool):
            if state:
                return f'*SET,PTT,OFF'
            else:
                return f'*SET,PTT,ON'
        ```
        """
        def toggle(func: Callable[[bool], str]):
            def nfunc(state: bool):
                if self.verbose: log.info(f"Executed {func(state)}")
                return func(state)
            self.elements[path] = Element(
                handler = nfunc,
                check_ack = check_ack,
                metadata = ToggleMetadata(
                    path=path,
                    element="toggle",
                    blocking=check_ack != None,
                    scope="local",
                    role=role,
                    method=method,
                    group=group,
                    sensible=sensible,
                    display_text=display_text if display_text else path.replace("_", " ").capitalize(),
                    tooltip=tooltip,
                    ref=ref,
                    colors=colors
                )
            )
            if self.verbose: log.info(f"{path} bound.")
            return nfunc
        return toggle
    
    def chatbox(
        self,
        path: str,
        ref: str = "general",
        check_ack: Callable[[str], bool] | None = None,
        role: Literal["operator", "admin"] = "operator",
        method: Literal["GET", "POST"] = "POST",
        group: str | None = None,
        sensible: bool = False,
        display_text: str | None = None,
        tooltip: str | None = None
    ):
        """
        Creates a chatbox (input and history) to handle text messages. You can specify a *ref* to filter where the messages come from/go to if your device supports multiple "channel-like" messaging.\n
        ### Params
        path: Name of the endpoint. Will then be accessible through `/action/{path}`. [REQUIRED].\n
        ref: Value bound to the origin/destination of the messages. Check full documentation for more info.\n
        role: Determine which role has access to this route.\n
        method: Define the HTTP method to which the API binds the action.\n
        check_ack: If specified, the SerialBridge will queue every other outgoing commands until the condition is fullfilled. Takes the read line as param.\n
        group: Specify the UI group to which the action belongs.\n
        sensible: Specify whether the action needs confirmation before executing.\n
        display_text: Name to display on the UI. If None, capitalize the *label* and replace every "_" with whitespaces.\n
        tooltip: Specify the on_hover tooltip.\n
        ### Decorated params
        msg: Message to send.\n
        ### Decorated return
        Your Serial command (as a *string*) for the specific *action*.
        ### Example
        ```
        @app.local.chatbox(
            path = "send_command",
            check_ack = lambda x: "ACK,OK" in x or "ACK,NG" in x,
            tooltip = "Send a command to the local radio."
            )
        def send_command(msg: str):
            return msg
        ```
        """
        def chatbox(func: Callable[[str], str]):
            def nfunc(msg: str):
                if self.verbose: log.info(f"Executed {func(msg)}")
                return func(msg)
            self.elements[path] = Element(
                handler = nfunc,
                check_ack = check_ack,
                metadata = ChatboxMetadata(
                    path=path,
                    element="chatbox",
                    blocking=check_ack != None,
                    scope="local",
                    role=role,
                    method=method,
                    group=group,
                    sensible=sensible,
                    display_text=display_text if display_text else path.replace("_", " ").capitalize(),
                    tooltip=tooltip,
                    ref=ref
                )
            )
            if self.verbose: log.info(f"{path} bound.")
            return nfunc
        return chatbox
    
    def text(
        self,
        path: str,
        check_ack: Callable[[str], bool] | None = None,
        role: Literal["operator", "admin"] = "operator",
        method: Literal["GET", "POST"] = "POST",
        group: str | None = None,
        sensible: bool = False,
        display_text: str | None = None,
        tooltip: str | None = None
    ):
        """
        Creates a text input to send texts to a remote entity.\n
        For managing messages with history, you'd want to use a Chatbox instead.\n
        ### Params
        path: Name of the endpoint. Will then be accessible through `/action/{path}`. [REQUIRED].\n
        role: Determine which role has access to this route.\n
        method: Define the HTTP method to which the API binds the action.\n
        check_ack: If specified, the SerialBridge will queue every other outgoing commands until the condition is fullfilled. Takes the read line as param.\n
        group: Specify the UI group to which the action belongs.\n
        sensible: Specify whether the action needs confirmation before executing.\n
        display_text: Name to display on the UI. If None, capitalize the *label* and replace every "_" with whitespaces.\n
        tooltip: Specify the on_hover tooltip.\n
        ### Decorated params
        msg: Message to send.\n
        ### Decorated return
        Your Serial command (as a *string*) for the specific *action*.
        ### Example
        ```
        @app.local.text(
            path = "set_ui_text",
            tooltip = "Set the radio UI text."
            )
        def set_ui_text(msg: str):
            return f'*SET,UI,TEXT,{msg}'
        ```
        """
        def text(func: Callable[[str], str]):
            def nfunc(msg: str):
                if self.verbose: log.info(f"Executed {func(msg)}")
                return func(msg)
            self.elements[path] = Element(
                handler = nfunc,
                check_ack = check_ack,
                metadata = GeneralMetadata(
                    path=path,
                    element="text",
                    blocking=check_ack != None,
                    scope="local",
                    role=role,
                    method=method,
                    group=group,
                    sensible=sensible,
                    display_text=display_text if display_text else path.replace("_", " ").capitalize(),
                    tooltip=tooltip,
                )
            )
            if self.verbose: log.info(f"{path} bound.")
            return nfunc
        return text
    
    def number(
        self,
        path: str,
        ref: str,
        vartype: Literal["int", "float"],
        min_max: tuple[int | float, int | float] | None = None,
        check_ack: Callable[[str], bool] | None = None,
        role: Literal["operator", "admin"] = "operator",
        method: Literal["GET", "POST"] = "POST",
        group: str | None = None,
        sensible: bool = False,
        display_text: str | None = None,
        tooltip: str | None = None
    ):
        """
        Creates a number input to send numeric values.\n
        Can be either int or float.\n
        ### Params
        path: Name of the endpoint. Will then be accessible through `/action/{path}`. [REQUIRED].\n
        ref: Value bound to the number input. Check full documentation for more info. [REQUIRED].\n
        vartype: Specify whether it's an int or a float. [REQUIRED].\n
        min_max: Minimum and maximum values (respectively) for the number input.\n
        role: Determine which role has access to this route.\n
        method: Define the HTTP method to which the API binds the action.\n
        check_ack: If specified, the SerialBridge will queue every other outgoing commands until the condition is fullfilled. Takes the read line as param.\n
        group: Specify the UI group to which the action belongs.\n
        sensible: Specify whether the action needs confirmation before executing.\n
        display_text: Name to display on the UI. If None, capitalize the *label* and replace every "_" with whitespaces.\n
        tooltip: Specify the on_hover tooltip.\n
        ### Decorated params
        value: Value sent.\n
        ### Decorated return
        Your Serial command (as a *string*) for the specific *action*.
        ### Example
        ```
        @app.local.number(
            path = "set_channel",
            ref = "channel",
            vartype = "int",
            min_max = (1, 16),
            tooltip = "Set the local channel."
            )
        def set_channel(value: int | float):
            return f'*SET,MCH,SEL,{value}'
        ```
        """
        def number(func: Callable[[int | float], str]):
            def nfunc(value: int | float):
                if self.verbose: log.info(f"Executed {func(value)}")
                return func(value)
            self.elements[path] = Element(
                handler = nfunc,
                check_ack = check_ack,
                metadata = NumberMetadata(
                    path=path,
                    element="number",
                    blocking=check_ack != None,
                    scope="local",
                    role=role,
                    method=method,
                    group=group,
                    sensible=sensible,
                    display_text=display_text if display_text else path.replace("_", " ").capitalize(),
                    tooltip=tooltip,
                    ref=ref,
                    vartype=vartype,
                    min_max=min_max
                )
            )
            if self.verbose: log.info(f"{path} bound.")
            return nfunc
        return number
    
    def dropdown(
        self,
        path: str,
        ref: str,
        values: list[str],
        check_ack: Callable[[str], bool] | None = None,
        role: Literal["operator", "admin"] = "operator",
        method: Literal["GET", "POST"] = "POST",
        group: str | None = None,
        sensible: bool = False,
        display_text: str | None = None,
        tooltip: str | None = None
    ):
        """
        Creates a dropdown that restrict the user to specific options.\n
        ### Params
        path: Name of the endpoint. Will then be accessible through `/action/{path}`. [REQUIRED].\n
        ref: Value bound to the dropdown. Check full documentation for more info. [REQUIRED].\n
        values: List of values (str) the dropdown has. [REQUIRED].\n
        role: Determine which role has access to this route.\n
        method: Define the HTTP method to which the API binds the action.\n
        check_ack: If specified, the SerialBridge will queue every other outgoing commands until the condition is fullfilled. Takes the read line as param.\n
        group: Specify the UI group to which the action belongs.\n
        sensible: Specify whether the action needs confirmation before executing.\n
        display_text: Name to display on the UI. If None, capitalize the *label* and replace every "_" with whitespaces.\n
        tooltip: Specify the on_hover tooltip.\n
        ### Decorated params
        value: Value sent.\n
        ### Decorated return
        Your Serial command (as a *string*) for the specific *action*.
        ### Example
        ```
        @app.local.dropdown(
            path = "set_channel",
            ref = "channel",
            values = ["2", "8", "24"],
            tooltip = "Set the local channel."
            )
        def set_channel(value: str):
            return f'*SET,MCH,SEL,{value}'
        ```
        """
        def dropdown(func: Callable[[str], str]):
            def nfunc(value: str):
                if self.verbose: log.info(f"Executed {func(value)}")
                return func(value)
            self.elements[path] = Element(
                handler = nfunc,
                check_ack = check_ack,
                metadata = DropdownMetadata(
                    path=path,
                    element="dropdown",
                    blocking=check_ack != None,
                    scope="local",
                    role=role,
                    method=method,
                    group=group,
                    sensible=sensible,
                    display_text=display_text if display_text else path.replace("_", " ").capitalize(),
                    tooltip=tooltip,
                    ref=ref,
                    values=values
                )
            )
            if self.verbose: log.info(f"{path} bound.")
            return nfunc
        return dropdown