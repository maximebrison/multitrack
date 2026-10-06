from typing import Callable
import logging
import asyncio

log = logging.getLogger("MultitrackBridge")

class MultitrackBridge():
    """
    Abstract class to bridge the MultitrackPlugin API to your Transceiver/Serial communication library. 
    """
    # Radio comm. handlers
    actions: dict[str, Callable[[str], None]] = {}
    send_text: Callable[[str, str], None] | None = None
    # Misc props
    polling_rate = 1

    def __init__(self):
        pass

    async def run(self, stop: asyncio.Event):
        while not stop.is_set():
            self.poll()
            await asyncio.sleep(self.polling_rate)

    def poll(self):
        """
        Method that is called every X seconds (defined in the *polling_rate* prop).\n
        Usually used for **getting data** from the radio
        """

    def stop(self):
        print("stop")

    def execute(self, action: str, target: str):
        try:
            self.actions[action](target)
            log.info(f"Executed {action} to {target}")
        except:
            log.error(f"Couldn't execute action: {action}")

    def bind_action(self, action: str, handler: Callable[[str], None]):
        self.actions[action] = handler

    def bind_text(self, handler: Callable[[str, str], None]):
        self.send_text = handler

    def available_actions(self):
        return list(self.actions.keys())

    def supports_text(self):
        return self.send_text != None