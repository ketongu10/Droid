
from threading import Thread

from RPI.control.main.monitoring.Profiler import Profiler
from RPI.control.main.network.server.SystemStream import SystemStream
from RPI.control.main.network.server.VideoStream import VideoStream
from RPI.control.main.monitoring.Debugger import Debugger
from time import time, sleep

from RPI.control.project_settings import RESOURCES


class ServerNetwork:

    def __init__(self, cfg, subscribers, hw_controller):
        self.credentials = cfg["PASSWORD"]
        self.synchronized_time = 0
        self.connected = False
        self.working = True
        self.abort_received = False
        self.system_stream = SystemStream(cfg, self)
        self.video_stream = VideoStream(cfg, self, hw_controller)
        self.subscribers = subscribers
        #self.wait_settings(subscribers)


    def check_settings(self) -> bool:
        data = self.system_stream.connection.recv(SystemStream.BUFFER_LEN)
        data = SystemStream.from_bytes(data)

        if data["title"] == "hello":
            if data["password"] == self.credentials:
                if self.validate_subscribers(data["subscribers"]):
                    self.synchronized_time = data["time"]
                    self.subscribers = data["subscribers"]
                    return True
        return False


    def start_session(self):
        self.system_stream.connection.sendall(SystemStream.to_bytes({
            "status": "approved",
            "errors": None
        }))
        video_conn, addr2 = self.video_stream.video_sock.accept()
        self.video_stream.connection = video_conn
        Debugger.RED().print(f"New video connection {addr2}")
        self.system_stream.working = True
        self.video_stream.working = True
        self.system_stream.system_thread.start()
        self.video_stream.video_thread.start()
        self.connected = True


    def deny_session(self):
        self.system_stream.connection.sendall(SystemStream.to_bytes({
            "status": "denied",
            "errors": "hz"
        }))
        self.system_stream.system_sock.close()

    def validate_subscribers(self, subs):
        return True


    def set_current_position(self, subscribers):
        self.system_stream.subscribers = subscribers



    def abort_connection(self, totaly=False):
        self.system_stream.working = False
        self.video_stream.working = False
        self.system_stream.system_thread.join()
        self.video_stream.video_thread.join()
        self.system_stream.system_thread = Thread(target=self.system_stream.read_from_system_stream)
        self.video_stream.video_thread = Thread(target=self.video_stream.handle_video_stream)
        self.system_stream.connection = None
        self.video_stream.connection = None
        self.system_stream.system_sock.listen()
        self.connected = False
        self.abort_received = False

        if totaly:
            self.working = False


