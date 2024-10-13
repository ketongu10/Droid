from RPI.control.client.monitoring.AbstractMonitoring import VACharacteristics
from RPI.control.client.monitoring.BodyPosition import BodyPosition
from RPI.control.client.monitoring.IPhysicalDevice import IPhysicalDevice
import json


class SystemMonitoring(IPhysicalDevice):
    def __init__(self):
        self.accumulator = VACharacteristics(100)
        self.body = BodyPosition()



if __name__ == "__main__":
    a = SystemMonitoring()
    print(len(json.dumps(a.get_subscribers())))



