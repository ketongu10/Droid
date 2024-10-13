

from RPI.control.client.monitoring.Debugger import Debugger
from RPI.control.client.monitoring.Profiler import Profiler, LazyMonitoring


def init_subscribers():
    Debugger.subscribers = [

    ]
    Profiler.subscribers["video_ping"] = LazyMonitoring()
