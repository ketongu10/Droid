from RPI.control.main.monitoring.SystemMonitoring import SystemMonitoring
from RPI.control.main.server.hardware.Interfaces.IExecuteOrders import IExecuteOrders
from RPI.control.main.server.hardware.Interfaces.IUseI2C import IUseI2C


class AccumulatorController(IUseI2C, IExecuteOrders):

    LEFT_BYTES = 0xfe
    RIGHT_BYTES = 0xff

    def get_full_current(self):
        ret = (self.bus.read_byte_data(self.malina_adr, AccumulatorController.LEFT_BYTES) * 255 +
               self.bus.read_byte_data(self.malina_adr, AccumulatorController.RIGHT_BYTES)) / 4096 * 3.3

        return f'{ret:.3f}'


    def carry_out_measurements(self, subscribers: SystemMonitoring) -> None:
        subscribers.accumulator.A.update_buffer(self.get_full_current())

