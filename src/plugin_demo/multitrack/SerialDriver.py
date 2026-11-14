from serial import Serial
from .models import CoreData
import logging
from datetime import datetime

log = logging.getLogger("SerialDriver")

class SerialDriver():
    """
    Abstract class that serves as a template for **Serial communication**.\n
    Here's how you write your driver :
    - Create a new class **inheriting** from this one
    - Overwrite the **parser()** method with your own
    - Provide a **Serial object** and specific **bol/eol** when initializing the class
    - Bind it to the **MultitrackAPI**
    """
    def __init__(self, serial: Serial, bol: bytes, eol: bytes, MSGCH: int = -1, DEFCH: int = -1, blocking_timeout: int = 5, verbose: bool = False):
        # Misc. properties
        self.verbose = verbose
        # Serial obj. and properties
        self.serial = serial
        self.bol = bol
        self.eol = eol
        self.MSGCH = MSGCH
        self.DEFCH = DEFCH
        self.blocking_timeout = blocking_timeout

    def on_startup(self) -> list[str]:
        """
        Actions executed when connecting to the serial port.
        """
        return []
    
    def set_plugin_id(self, id: str):
        self.plugin_id = id
    
    def parser(self, cmd: str) -> CoreData:
        """
        Place here every **command** your radio may receive.\n
        Returns sanitized **PluginData** for the *Core*
        """
        return CoreData(
            plugin_id=self.plugin_id,
            entity_id=None,
            timestamp=datetime.now().timestamp(),
            type="err",
            success=False,
            data=None
        )

    def nmea_to_decimal(self, value: str, hemisphere: str):
        """
        Small utility to convert **NMEA** coordinates to **decimal**.
        """
        dot = value.index(".")
        degrees = int(value[:dot - 2])
        minutes = float(value[dot - 2:])
        dec = degrees + minutes / 60
        return -dec if hemisphere in ("S", "W") else dec

    def encode_wrap(self, cmd: str):
        """
        Encode the command in utf-8, then wraps it with *bol* and *eol* characters.
        """
        return self.bol + cmd.encode() + self.eol