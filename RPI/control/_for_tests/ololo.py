import inspect
from RPI.control.client.monitoring.Debugger import Debugger
from RPI.control.client.monitoring.Profiler import Profiler


class A:
    def a(self):
        return 1


class B:
    def __init__(self):
        self.b = A()

bb = B()

print(bb.b.a())

for key, value in bb.__dict__.items():
    print(value.a(), value)