from .SerialDriver import SerialDriver
import logging
import asyncio, threading, queue, time

log = logging.getLogger("SerialBridge")

class SerialBridge():
    """
    Bridges the MultitrackAPI and the SerialDriver.
    """
    def __init__(self, driver: SerialDriver):
        self.loop: asyncio.AbstractEventLoop
        self.stop_sig = threading.Event()
        self.commands = queue.Queue()
        self.events = asyncio.Queue()
        self.thread = threading.Thread(target=self._run)
        self.driver = driver

    def _run(self):
        while not self.stop_sig.is_set():
            time.sleep(0.5) # Simulate read on radio (getMessage)
            self.driver.receive_command()
            self.loop.call_soon_threadsafe(self.events.put_nowait, "Reading from radio")

            while not self.commands.empty():
                cmd, fut = self.commands.get_nowait()
                time.sleep(0.2) # Simulate action execution
                self.driver.send_command(cmd)
                self.loop.call_soon_threadsafe(fut.set_result, f"Executed {cmd}")

    async def send_command(self, cmd: str):
        fut = self.loop.create_future()
        self.commands.put((cmd, fut))
        print(await fut)

    def bind_loop(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop