from picamera2 import Picamera2, Preview
from libcamera import ColorSpace
from pprint import *
import time
import io
import numpy as np

from RPI.control.main.network.AbstractStream import AbstractStream
from RPI.control.main.server.hardware.Interfaces.IDevice import IDevice

MAX_SIZE = 2592, 1944
NOW_SIZE = 768, 768
MIN_SIZE = 650, 650
HEADERSIZE = 10


class CameraController(AbstractStream, IDevice):

    def __init__(self, cfg):
        self.picam2 = Picamera2()
        self.camera_config = self.picam2.create_still_configuration(main={"size": [int(cfg["IMAGE_SIZE"])]*2},
                                                                    lores={"size": [int(cfg["IMAGE_SIZE"])]*2},
                                                                    display=None,
                                                                    colour_space=ColorSpace.Sycc()
                                                                    )
        self.picam2.configure(self.camera_config)
        self.picam2.start()

    def _get_view(self):
        image_data = io.BytesIO()
        self.picam2.capture_file(image_data, format='jpeg')

        msg = bytes(image_data.getbuffer())
        return bytes(f"{len(msg):<{AbstractStream.HEADER_SIZE}}", 'utf-8') + msg

    def finalize(self):
        self.picam2.stop()


if __name__ == "__main__":
    cam = CameraController({"IMAGE_SIZE": NOW_SIZE})
    cam.picam2.start_preview(Preview.QTGL) #DRM)
    pprint(cam.picam2.sensor_modes)
    cam.picam2.start()
    time.sleep(1)
    cam.picam2.set_controls({"AfMode": 0,  "LensPosition": 0, "AfTrigger": 1})
    cam.picam2.stop()
    cam.picam2.capture_file("/home/master/control/test000.jpg")
