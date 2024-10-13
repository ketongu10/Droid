
import socket
import json
from threading import Thread
from RPI.control.client.network.AbstractStream import AbstractStream
from RPI.control.client.monitoring.Debugger import Debugger


class SystemAbstractStream(AbstractStream):
    def __init__(self, cfg):
        self.working = False
        self.received_data: dict = None
        self.system_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.system_sock.connect((cfg["HOST"], cfg["GEN_PORT"]))
        self.system_thread = Thread(target=self.read_from_system_stream)

    def read_from_system_stream(self):
        while self.working:
            message = json.dumps({
                "title": "get_system_info",
            })
            Debugger.print(message)
            self.system_sock.sendall(SystemAbstractStream.to_bytes(message))
            data = self.system_sock.recv(SystemAbstractStream.BUFFER_LEN)
            data = SystemAbstractStream.from_bytes(data)
            Debugger.print(data)
            if data["title"] == "system_info":
                self.received_data = data
                #print(f"PING logs: {time()-t0}")

    def parse_incoming_message(self, message):
        return {}

    def move(self, side):
        message = json.dumps({
            "title": "command",
            "command": "should_move",
            "move": side
        })
        Debugger.print(message)
        self.system_sock.send(SystemAbstractStream.to_bytes(message))

    def move_arm(self, mode):
        message = json.dumps({
            "title": "command",
            "command": "arm_move",
            "move": mode
        })
        Debugger.print(message)
        self.system_sock.send(SystemAbstractStream.to_bytes(message))

    def change_speeds(self, mode):
        message = json.dumps({
            "title": "command",
            "command": "change_speed",
            "move": mode
        })
        Debugger.print(message)
        self.system_sock.send(SystemAbstractStream.to_bytes(message))
