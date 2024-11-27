import json
from RPI.control.main.monitoring.Debugger import Debugger
from time import time, sleep

class AbstractStream:
    BUFFER_LEN = 2048 #4096
    VIDEO_BUFFER_LEN = 64
    HEADER_SIZE = 10
    ELINER = '`'

    @staticmethod
    def to_bytes(message: dict | str) -> bytes:
        if isinstance(message, dict):
            return bytes(json.dumps(message).ljust(AbstractStream.BUFFER_LEN, AbstractStream.ELINER), 'UTF-8')
        if isinstance(message, str):
            Debugger.print(message)
            return bytes(message.ljust(AbstractStream.BUFFER_LEN, AbstractStream.ELINER), 'UTF-8')
        raise AttributeError

    @staticmethod
    def from_bytes(buffer: bytes):
        Debugger.print(len(buffer), buffer)
        return json.loads(buffer.replace(bytes(AbstractStream.ELINER, 'UTF-8'), bytes('', 'UTF-8')))

    @staticmethod
    def recv(socket, buflen):
        data = b''
        while len(data) < buflen:
            data += socket.recv(buflen-len(data))
        return data

    @staticmethod
    def maintain_fps(func, dt):
        t0 = time()
        func()
        t = time() - t0
        if t < dt:
            sleep(dt - t)


if __name__ == "__main__":
    a = AbstractStream()
    print(a.from_bytes(a.to_bytes({"1": [1, 2]})))
