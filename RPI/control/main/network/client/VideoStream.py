import socket
import json
from threading import Thread
from time import sleep, time
from RPI.control.main.monitoring.Debugger import Debugger
from RPI.control.main.monitoring.Profiler import Profiler
from RPI.control.main.network.AbstractStream import AbstractStream


class VideoStream(AbstractStream):

    def __init__(self, cfg, network, fps=20):
        self.working = False
        self.dt = 1/fps
        self.received_data = None
        self.network = network
        self.video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cfg = cfg
        self.video_thread = Thread(target=self.read_from_video_stream)

    def read_from_video_stream(self):
        while self.working:
            try:
                #sleep(self.dt)
                VideoStream.maintain_fps(self._read_from_video_stream, self.dt)
            except Exception as e:
                print(f"ClientVideoStream: {e}")
                self.network.abort_received = True
                break

    @Profiler.register("video_ping")
    def _read_from_video_stream(self):
        self.video_sock.sendall(bytes(json.dumps({
            "title": "get_image",
        }), 'UTF-8'))

        full_msg = b''
        new_msg = True
        t0_rec = time()
        while True:
            msg = self.video_sock.recv(1024)  # 32768)
            if msg != b'':
                if new_msg:
                    # if len(msg) == 0:
                    #     print(msg)
                    #     break
                    msglen = int(msg[:VideoStream.HEADER_SIZE])
                    new_msg = False

                full_msg += msg
                if len(full_msg) - VideoStream.HEADER_SIZE == msglen:
                    new_msg = True
                    Debugger.print(f"RECEIVING TIME={time() - t0_rec}, MESSAGE LEN={msglen}")
                    Profiler.profile({"rec_time": (time() - t0_rec) * 1000})
                    self.received_data = full_msg[VideoStream.HEADER_SIZE:]
                    break
                elif len(full_msg) - VideoStream.HEADER_SIZE > msglen:
                    break


    def start_video_thread(self):
        self.video_sock.connect((self.cfg["HOST"], self.cfg["VIDEO_PORT"]))
        self.video_thread.start()
