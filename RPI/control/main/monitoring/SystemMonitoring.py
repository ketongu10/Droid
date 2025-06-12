from time import time

from RPI.control.main.monitoring.AbstractMonitoring import VACharacteristics, AbstractMonitor
from RPI.control.main.monitoring.BodyPosition import BodyPosition
from RPI.control.main.monitoring.IPhysicalDevice import IPhysicalDevice
from RPI.control.project_settings import SHM_CLIENT_SYSSTR_TIME
import json

from RPI.control.main.monitoring.Profiler import Profiler
from RPI.control.main.network.Side import Side


class SystemMonitoring(IPhysicalDevice):
    def __init__(self, side=Side.Client):
        self.accumulator = VACharacteristics(100, V_bounds=(0, 20), A_bounds=(0, 3), side=side)
        self.body = BodyPosition(side)
        self.initial_time = time()
        self.time = AbstractMonitor(100, side=side,
                                          sh_mem_name=(SHM_CLIENT_SYSSTR_TIME if side == Side.Client else None))
        self.subscribers = self.get_subscribers()

    @Profiler.register('SystemMonitoring.update_subscribers')
    def update_subscribers(self):
        self.subscribers['accumulator'] = self.accumulator.get_subscribers()
        self.subscribers['body'] = self.body.get_subscribers()
        self.subscribers['time'] = str(self.time.last())

    def get_subscribers(self) -> dict:
        return {
                "time": str(self.time.last()),
                "accumulator": self.accumulator.get_subscribers(),
                "body": self.body.get_subscribers(),
                }


    def set_subscription_values(self, parameters: dict):
        if parameters:
            self.time.update_buffer(parameters["time"])
            self.accumulator.set_subscription_values(parameters['accumulator'])
            self.body.set_subscription_values(parameters['body'])

if __name__ == "__main__":
    a = SystemMonitoring()
    t0 = time()
    print(len(json.dumps(a.get_subscribers())))
    print(time()-t0)
    print(a.get_subscribers())



