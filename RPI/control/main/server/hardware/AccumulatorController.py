from RPI.control.main.monitoring.SystemMonitoring import SystemMonitoring
from RPI.control.main.server.hardware.Interfaces.IExecuteOrders import IExecuteOrders
from RPI.control.main.server.hardware.Interfaces.IUseI2C import IUseI2C


class AccumulatorController(IUseI2C, IExecuteOrders):

    LEFT_BYTES_A = 0xfe
    RIGHT_BYTES_A = 0xff
    LEFT_BYTES_V = 0xfe-16
    RIGHT_BYTES_V = 0xff-16

    A_CONST = 4.216 # EXPERIMENTAL
    V_CONST = 6

    def get_full_current(self):
        ret = AccumulatorController.A_CONST * (2.5 - (self.bus.read_byte_data(self.malina_adr, AccumulatorController.LEFT_BYTES_A) * 255 +
               self.bus.read_byte_data(self.malina_adr, AccumulatorController.RIGHT_BYTES_A)) / 4096 * 3.3)

        return f'{ret:.3f}'

    def get_full_voltage(self):
        ret = AccumulatorController.V_CONST * (self.bus.read_byte_data(self.malina_adr, AccumulatorController.LEFT_BYTES_V) * 255 +
               self.bus.read_byte_data(self.malina_adr, AccumulatorController.RIGHT_BYTES_V)) / 4096 * 3.3

        return f'{ret:.3f}'


    def carry_out_measurements(self, subscribers: SystemMonitoring) -> None:
        subscribers.accumulator.A.update_buffer(self.get_full_current())
        subscribers.accumulator.V.update_buffer(self.get_full_voltage())

