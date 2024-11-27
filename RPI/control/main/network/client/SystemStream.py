
import socket
import json
import sys
from multiprocessing.shared_memory import SharedMemory
from threading import Thread
from time import time, sleep

import numpy as np

from RPI.control.main.monitoring.Profiler import Profiler
from RPI.control.main.network.AbstractStream import AbstractStream
from RPI.control.main.monitoring.Debugger import Debugger
from RPI.control.project_settings import SHM_CLIENT_SYSSTR_TIME


class SystemStream(AbstractStream):
    def __init__(self, cfg, network, fps=20):
        self.working = False
        self.dt = 1/fps
        self.received_data: dict = {"subscribers": {}}
        self.received_time_shm = SharedMemory(name=SHM_CLIENT_SYSSTR_TIME, create=True, size=4*100)
        self.received_time = np.ndarray(shape=(100, ), dtype=np.float32, buffer=self.received_time_shm.buf)
        self.network = network
        self.system_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.system_sock.connect((cfg["HOST"], cfg["GEN_PORT"]))
        self.system_thread = Thread(target=self.read_from_system_stream)

    def read_from_system_stream(self):
        while self.working:
            try:
                #sleep(self.dt)
                SystemStream.maintain_fps(self._read_from_system_stream, self.dt)
            except Exception as e:
                print(f"ClientSystemStream: {e}")
                self.network.abort_received = True
                break

    @Profiler.register("read_sys_stream")
    def _read_from_system_stream(self):
        message = json.dumps({
            "title": "get_system_info",
        })
        Debugger.print(message)
        t0 = time()
        self.system_sock.sendall(SystemStream.to_bytes(message))
        data = SystemStream.recv(self.system_sock, SystemStream.BUFFER_LEN)
        rec_time = time()
        Profiler.profile({"system_ping": (rec_time-t0)*1000})
        data = SystemStream.from_bytes(data)
        Debugger.print(data)

        if data["title"] == "system_info":
            self.received_data = data
            self.received_time[:-1] = self.received_time[1:]
            self.received_time[-1] = rec_time - self.network.initial_time

    def parse_incoming_message(self, message):
        return {}

    def move(self, side):
        message = json.dumps({
            "title": "command",
            "command": "should_move",
            "move": side
        })
        Debugger.print(message)
        self.system_sock.send(SystemStream.to_bytes(message))

    def move_arm(self, mode):
        message = json.dumps({
            "title": "command",
            "command": "arm_move",
            "move": mode
        })
        Debugger.print(message)
        self.system_sock.send(SystemStream.to_bytes(message))

    def change_speeds(self, mode):
        message = json.dumps({
            "title": "command",
            "command": "change_speeds",
            "move": mode
        })
        Debugger.print(message)
        print("dawdwa", mode)
        self.system_sock.send(SystemStream.to_bytes(message))
