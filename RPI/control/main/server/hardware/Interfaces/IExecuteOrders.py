from RPI.control.main.monitoring.SystemMonitoring import SystemMonitoring
from RPI.control.main.server.hardware.Orders import Orders


class IExecuteOrders:

    def execute_orders(self, orders: Orders) -> None: pass

    def carry_out_measurements(self, subscribers: SystemMonitoring) -> None: pass

