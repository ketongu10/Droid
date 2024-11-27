from RPI.control.main.monitoring.Debugger import Debugger


class IUseI2C:
    DEFAULT_CHECK_POINT = 0x55

    def __init__(self, bus, adr):
        self.bus = bus.instance
        self.malina_adr = adr


    def is_available(self):
        try:
            self.bus.read_byte_data(self.malina_adr, IUseI2C.DEFAULT_CHECK_POINT)
            return True
        except Exception as e:
            Debugger.RED().print(f'{self.malina_adr} is not available')
            return False
