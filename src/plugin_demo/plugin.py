from multitrack import MultitrackAPI, SerialBridge, SerialDriver, BaseActionModel, BaseTextModel, ChannelModel
from serial import Serial

class ICOMDriver(SerialDriver):
    def demux(self, cmd: str):
        print(cmd)

driver = ICOMDriver(
    serial=Serial(),
    bol=b"\x02",
    eol=b"\x03"
)

@driver.action(label="kill")
def kill(p: BaseActionModel):
    return f"Killing {p.target}"

@driver.action(label="stun")
def stun(p: BaseActionModel):
    return f"*SET,IDAS,TXSTUN,IND,{p.target}"

@driver.action(label="revive")
def revive(p: BaseActionModel):
    return f"Reviving {p.target}"

@driver.action(label="get_status")
def get_status(p: BaseActionModel):
    return f"Getting status from {p.target}"

@driver.action(label="get_position")
def get_position(p: BaseActionModel):
    return f"Getting position from {p.target}"

@driver.action(label="send_text")
def send_text(p: BaseTextModel):
    return f"Sending {p.msg} to {p.target}"

@driver.action(label="get_channel", scope="local", method="GET")
def get_channel():
    return '*GET,MCH,SEL'

@driver.action(label="set_channel", scope="local")
def set_channel(p: ChannelModel):
    return f'*SET,MCH,SEL,{p.channel}'

bridge = SerialBridge(
    driver=driver
)

app = MultitrackAPI(
    http_port=5131,
    discovery_port=5130,
    discovery_msg="multitrack",
    bridge=bridge
)

if __name__ == "__main__":
    app.run()