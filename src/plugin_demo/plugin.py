from multitrack import MultitrackAPI, SerialDriver, CoreData, GPSPosition, TextMessage, StatusUpdate, EntityInfo
from serial import Serial
from datetime import datetime

class ICOMDriver(SerialDriver):
    def __init__(self, serial: Serial, bol: bytes, eol: bytes, local_id: int, MSGCH: int = -1, DEFCH: int = -1, blocking_timeout: int = 5, verbose: bool = False):
        super().__init__(serial, bol, eol, MSGCH, DEFCH, blocking_timeout, verbose)
        self.local_id = local_id

    def on_startup(self) -> list[str]:
        return [
            f'*SET,IDAS,SENDID,TG,9900,{self.local_id}',
            '*GET,IDAS,SENDID,TG'
        ]

    def parser(self, cmd: str):
        cmds = cmd.split(",")
        match(cmds[2]):
            case "GPS":
                return CoreData(
                    plugin_id=self.plugin_id,
                    entity_id=cmds[3],
                    timestamp=datetime.now().timestamp()*1000,
                    type="gps",
                    success="OK" in cmds[7],
                    data=GPSPosition(
                        latitude=float(cmds[4]),
                        longitude=float(cmds[5])
                    )
                )
            case "TXMSG":
                return CoreData(
                    plugin_id=self.plugin_id,
                    entity_id=cmds[3],
                    timestamp=datetime.now().timestamp()*1000,
                    type="text",
                    success="OK" in cmds[6],
                    data=TextMessage(
                        msg=cmds[4]
                    )
                )
            case "STATUS":
                return CoreData(
                    plugin_id=self.plugin_id,
                    entity_id=cmds[3],
                    timestamp=datetime.now().timestamp()*1000,
                    type="status",
                    success="OK" in cmds[6],
                    data=StatusUpdate(
                        status=cmds[4]
                    )
                )
            case _:
                return CoreData(
                    plugin_id=self.plugin_id,
                    entity_id=None,
                    timestamp=datetime.now().timestamp()*1000,
                    type="err",
                    success=False,
                    data=None
                )

driver = ICOMDriver(
    serial=Serial("COM5", 9600, timeout=1),
    bol=b"\x02",
    eol=b"\x03",
    local_id=65501
    )

app = MultitrackAPI(
    http_port=5131,
    discovery_port=5130,
    discovery_msg="multitrack",
    driver=driver,
    listening_interface="192.168.1.21"
    )

@app.remote.button(
    path="stun"
    )
def stun(e: EntityInfo):
    return f"*SET,IDAS,TXSTUN,IND,{e.serial}"

@app.remote.button(
    path="revive"
    )
def revive(e: EntityInfo):
    return f"*SET,IDAS,TXREVIVE,IND,{e.serial}"

@app.remote.button(
    path="get_position",
    check_ack=lambda x: "ACK,OK" in x or "ACK,NG" in x
    )
def get_position(e: EntityInfo):
    return f'*SET,IDAS,TXSTAT,IND,{e.serial},{driver.local_id},24'

@app.remote.chatbox(
    path="send_message"
    )
def send_message(e: EntityInfo, msg: str):
    return f'*SET,IDAS,TXMSG,IND,{e.serial},{driver.local_id},MSG,"{msg.replace("\"", "\'")}"'

@app.local.number(
    path="set_local_channel",
    ref="local_channel",
    vartype="int",
)
def set_local_channel(value: int | float):
    return f"*SET,MCH,SEL,{value}"

if __name__ == "__main__":
    app.run()