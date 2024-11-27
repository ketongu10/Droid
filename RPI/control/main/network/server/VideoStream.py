
import socket
import json
from threading import Thread
from time import sleep

from RPI.control.main.monitoring.Profiler import Profiler
from RPI.control.main.network.AbstractStream import AbstractStream
from RPI.control.project_settings import RESOURCES
from PIL import Image
from RPI.control.main.server.hardware.Orders import Orders
from RPI.control.main.monitoring.Debugger import Debugger
import io

class VideoStream(AbstractStream):


    def __init__(self, cfg, server_network, hw_controller):
        self.working = False
        self.subscribers = None
        self.connection = None
        self.server_network = server_network
        self.video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_sock.bind((cfg["HOST"], cfg["VIDEO_PORT"]))
        self.video_sock.listen(1)
        self.video_thread = Thread(target=self.handle_video_stream)
        self.get_view = self._get_view if not hw_controller.camera_is_available else hw_controller.camera._get_view

    def handle_video_stream(self):
        while self.working:
            try:
                data = self.connection.recv(VideoStream.VIDEO_BUFFER_LEN)
                data = json.loads(data.decode('utf-8'))
                if data["title"] == "get_image":
                    self.connection.sendall(self.get_view())
                    """conn.sendall(bytes(json.dumps({
                         "response": self.players
                     }), 'UTF-8'))"""
            except Exception as e:
                Debugger.RED().print(f"ServerVideoStream: {e}")
                self.server_network.abort_received = True
                break

        Debugger.GREEN().print("Server video stream finished working")

    @Profiler.register("VideoStream.get_view")
    def _get_view(self):
        # picam2.capture_file("test11.jpg")
        img = Image.open(RESOURCES/"image_received2.png")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes = img_bytes.getvalue()
        msg = bytes(img_bytes)
        return bytes(f"{len(msg):<{VideoStream.HEADER_SIZE}}", 'utf-8') + msg