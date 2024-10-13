import io
import socket
import json
from time import time
from RPI.control.client.network.SystemStream import SystemAbstractStream
from RPI.control.client.network.VideoStream import VideoStream
from RPI.control.client.monitoring.Debugger import Debugger


class Network:
    def __init__(self, cfg, subscribers):
        self.credentials = cfg["PASSWORD"]
        self.initial_time = time()
        self.system_stream = SystemAbstractStream(cfg)
        self.video_stream = VideoStream(cfg)
        self.define_settings(subscribers)

    def send_commands_to_server(self, control_inputs: dict):
        self.system_stream.move(control_inputs["trucks_movements"])
        self.system_stream.move_arm(control_inputs["arm_movements"])
        speed_mode = control_inputs["change_speeds"]
        if speed_mode is not None:
            self.system_stream.change_speeds(speed_mode)

    def define_settings(self, subscribers: list):
        self.system_stream.system_sock.send(SystemAbstractStream.to_bytes({
            "title": "hello",
            "time": self.initial_time,
            "password": self.credentials,
            "subscribers": subscribers
        }))
        data = self.system_stream.system_sock.recv(SystemAbstractStream.BUFFER_LEN)
        data = SystemAbstractStream.from_bytes(data)
        if data.get("status") and data["status"] == "approved":
            self.system_stream.working = True
            self.video_stream.working = True
            self.system_stream.system_thread.start()
            self.video_stream.video_thread.start()
        elif data.get("status") and data["status"] == "denied":
            if data.get("errors"):
                raise Exception.with_traceback(tb=data["errors"])
            else:
                raise Exception.with_traceback(tb="Unknown Server error during establishing connection")
        else:
            raise Exception.with_traceback(tb="Unknown Server error during establishing connection")

    def abort_connection(self, error="planned_finishing"):

        self.system_stream.working = False
        self.video_stream.working = False
        self.system_stream.system_thread.join()
        self.video_stream.video_thread.join()
        self.system_stream.system_sock.send(SystemAbstractStream.to_bytes({
            "title": "goodbye",
            "error": error
        }))
        self.system_stream.system_sock.close()
        self.video_stream.video_sock.close()


