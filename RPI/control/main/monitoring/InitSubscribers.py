

from RPI.control.main.monitoring.Debugger import Debugger
from RPI.control.main.monitoring.Profiler import Profiler, LazyMonitoring
from RPI.control.main.network.Side import Side
from RPI.control.project_settings import RUNS
from datetime import datetime
import sys

def init_subscribers(side=Side.Client):
    if side == Side.Client:
        Debugger.setup_stdout()
        Debugger.setup_output(RUNS/f"client/{str(datetime.now().time()).replace(':', '-')}.txt")
        Debugger.subscribers = [

            #'AbstractStream.to_bytes',
            #'AbstractStream.from_bytes',
            'AbstractStream.maintain_fps',
            # 'VideoStream._read_from_video_stream',
            'SystemStream.change_speeds',
            #'SystemStream.move',
            'Network.start_session'
        ]
        Profiler.subscribers["video_ping"] = LazyMonitoring()
        Profiler.subscribers["rec_time"] = LazyMonitoring()
        Profiler.subscribers["system_ping"] = LazyMonitoring()

    if side == Side.Server:
        Debugger.setup_stdout()
        Debugger.setup_output(RUNS/f"server/{str(datetime.now().time()).replace(':', '-')}.txt")
        Debugger.subscribers = [
            #'AbstractStream.to_bytes',
            #'AbstractStream.from_bytes',
            'SystemStream.change_speeds',
            'ServerNetwork.start_session',
            #'VideoStream.handle_video_stream',
            #'SystemStream.read_from_system_stream',
            'Server.listen',
            'HWController.__init__',
            'ArmController.is_available',
            'ArmController.execute_orders'
        ]

        #Profiler.subscribers["system_ping"] = LazyMonitoring()
