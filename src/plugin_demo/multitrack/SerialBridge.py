from .SerialDriver import SerialDriver
from typing import Callable
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
        self.commands: queue.Queue[tuple[str, Callable[[str], bool] | None, asyncio.Future]] = queue.Queue()
        self.events = asyncio.Queue()
        self.thread = threading.Thread(target=self._run)
        self.driver = driver

    def _run(self):
        line = b''
        busy: float | None = None
        predicate: Callable[[str], bool] | None = None
        while not self.stop_sig.is_set():
            # Read a byte from the Serial object init. in the driver
            byte_read = self.driver.serial.read(1)

            # Resets the line when a 'bol' is found
            if byte_read == self.driver.bol:
                line = b''
            else:
                if byte_read == self.driver.eol:
                    # Checks for the ACK, sets the busy flag to None if the condition is fullfilled
                    if predicate and predicate(line.decode()):
                        busy = None

                    self.loop.call_soon_threadsafe(log.info, f"Received {line.decode()}")
                else:
                    # Add the byte read to the line
                    line += byte_read

            # Manages the writing of serial commands
            while not self.commands.empty() and not busy:
                cmd, ack, fut = self.commands.get_nowait()

                # If the commands has to wait for a provided ACK, set the ok flag to False
                if ack:
                    predicate = ack
                    busy = time.time()

                # Write the command on the serial port and returns the result via the Future object
                self.driver.serial.write(self.driver.encode_wrap(cmd))
                self.loop.call_soon_threadsafe(fut.set_result, f"Sent {cmd}")

    async def send_command(self, cmd: str, ack: Callable[[str], bool] | None = None):
        fut = self.loop.create_future()
        self.commands.put((cmd, ack, fut))
        log.info(await fut)

    def bind_loop(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop