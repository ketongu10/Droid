from smbus import SMBus

from RPI.control.main.server.hardware.Interfaces.IDevice import IDevice


class I2CBus(IDevice):

    def __init__(self, id_):
        self.instance = SMBus(id_)

    def finalize(self):
        self.instance.close()
