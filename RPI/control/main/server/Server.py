import os
import sys

import numpy as np

from RPI.control.main.monitoring.Profiler import Profiler
from RPI.control.main.network.Side import Side
from RPI.control.main.network.server.ServerNetwork import ServerNetwork
from RPI.control.main.monitoring.SystemMonitoring import SystemMonitoring
from RPI.control.main.monitoring.Debugger import Debugger
from RPI.control.main.monitoring.InitSubscribers import init_subscribers
from RPI.control.main.server.hardware.HWController import HWController
from RPI.control.project_settings import RESOURCES
from time import time
import yaml




class Server:
    FPS = 120
    system_monitoring: SystemMonitoring | None
    hw_controller: HWController | None
    network: ServerNetwork | None
    working = True

    @staticmethod
    def initial_setup():
        sys.setswitchinterval(0.005)
        init_subscribers(side=Side.Server)
        with open(RESOURCES/'config.yml', 'r') as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
        Server.system_monitoring = SystemMonitoring(side=Side.Server)
        Server.hw_controller = HWController(cfg, Server.system_monitoring, Server.FPS)
        Server.network = ServerNetwork(cfg, Server.system_monitoring.get_subscribers(), Server.hw_controller)



    @staticmethod
    def listen():
        try:
            while Server.working:
                if not Server.network.connected:
                    system_conn, addr1 = Server.network.system_stream.system_sock.accept()
                    Server.network.system_stream.connection = system_conn
                    Debugger.print("New connection", addr1)
                    if Server.network.check_settings():
                        Server.network.start_session()
                        Server.network.system_stream.subscribers = Server.system_monitoring.subscribers  # WARNING UPDATE DICT VALUES, NOT THE WHOLE DICT
                        Server.hw_controller.orders = Server.network.system_stream.received_orders
                    else:
                        Server.network.deny_session()
                elif Server.network.abort_received:
                    Server.network.abort_connection()
                else:
                    Profiler.dump(RESOURCES / "prof_server.txt", full_info=True)
        except KeyboardInterrupt:
            Server.hw_controller.finalize()
        finally:
            Server.hw_controller.finalize()




def main():
    Server.initial_setup()
    Server.listen()


if __name__ == "__main__":
    main()
