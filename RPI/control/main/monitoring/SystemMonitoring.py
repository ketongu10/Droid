from time import time

from RPI.control.main.monitoring.AbstractMonitoring import VACharacteristics
from RPI.control.main.monitoring.BodyPosition import BodyPosition
from RPI.control.main.monitoring.IPhysicalDevice import IPhysicalDevice
import json

from RPI.control.main.monitoring.Profiler import Profiler
from RPI.control.main.network.Side import Side


class SystemMonitoring(IPhysicalDevice):
    def __init__(self, side=Side.Client):

        self.accumulator = VACharacteristics(100, V_bounds=(0, 20), A_bounds=(0, 3), side=side)
        self.body = BodyPosition(side)
        self.subscribers = self.get_subscribers()

    @Profiler.register('SystemMonitoring.update_subscribers')
    def update_subscribers(self):
        self.subscribers['accumulator'] = self.accumulator.get_subscribers()
        self.subscribers['body'] = self.body.get_subscribers()

if __name__ == "__main__":
    a = SystemMonitoring()
    t0 = time()
    print(len(json.dumps(a.get_subscribers())))
    print(time()-t0)
    print(a.get_subscribers())



