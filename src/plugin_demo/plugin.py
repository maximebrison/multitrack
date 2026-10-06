from multitrack import MultitrackPlugin
from multitrack.MultitrackBridge import MultitrackBridge

class Bridge(MultitrackBridge):
    polling_rate = 0.5
    def poll(self):
        print("hey")

bridge = Bridge()

bridge.bind_action(
    "kill",
    lambda target : print(f"kill {target}")
)

bridge.bind_action(
    "stun",
    lambda target : print(f"stun {target}")
)

bridge.bind_action(
    "revive",
    lambda target : print(f"revive {target}")
)

bridge.bind_action(
    "get_status",
    lambda target : print(f"requesting status from {target}")
)

bridge.bind_action(
    "get_position",
    lambda target : print(f"requesting position from {target}")
)

bridge.bind_text(
    lambda target, text :
        print(f"sending {text} to {target}")
)

app = MultitrackPlugin(
    http_port=5131,
    discovery_port=5130,
    discovery_msg="multitrack",
    bridge=bridge
)

if __name__ == "__main__":
    app.run()