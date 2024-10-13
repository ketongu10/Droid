import socket
import json
from threading import Thread
from time import sleep, time
from RPI.control.client.monitoring.Debugger import Debugger
from RPI.control.client.monitoring.Profiler import Profiler


class VideoStream:

    HEADER_SIZE = 10

    def __init__(self, cfg):
        self.working = False
        self.received_data = None
        self.video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_sock.connect((cfg["HOST"], cfg["VIDEO_PORT"]))
        self.video_thread = Thread(target=self.read_from_video_stream)

    def read_from_video_stream(self):
        while self.working:
            t0_ping = time()
            self.video_sock.sendall(bytes(json.dumps({
                "title": "get_image",
            }), 'UTF-8'))

            full_msg = b''
            new_msg = True
            t0 = time()
            while True:
                msg = self.video_sock.recv(1024)  # 32768)
                if new_msg:

                    msglen = int(msg[:VideoStream.HEADER_SIZE])
                    new_msg = False


                full_msg += msg

                # print(len(full_msg))

                if len(full_msg) - VideoStream.HEADER_SIZE == msglen:
                    new_msg = True
                    Debugger.print(f"RECEIVING TIME={time() - t0}, MESSAGE LEN={msglen}")
                    Profiler.profile({"video_ping": time() - t0_ping})
                    self.received_data = full_msg[VideoStream.HEADER_SIZE:]
                    break
                elif len(full_msg) - VideoStream.HEADER_SIZE > msglen:
                    break
            # print("finished circle")


