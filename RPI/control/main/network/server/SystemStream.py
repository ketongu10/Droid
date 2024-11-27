
import socket
import json
import sys
from threading import Thread
from RPI.control.main.network.AbstractStream import AbstractStream
from RPI.control.main.server.hardware.Orders import Orders
from RPI.control.main.monitoring.Debugger import Debugger

class SystemStream(AbstractStream):

    def __init__(self, cfg, server_network):
        self.working = False
        self.received_orders = Orders()
        self.server_network = server_network
        self.subscribers = {}
        self.connection = None
        self.system_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.system_sock.bind((cfg["HOST"], cfg["GEN_PORT"]))
        self.system_sock.listen(1)
        self.system_thread = Thread(target=self.read_from_system_stream)

    def read_from_system_stream(self):
        while self.working:
            try:
                data = SystemStream.recv(self.connection, SystemStream.BUFFER_LEN)
                data = SystemStream.from_bytes(data)
                if data["title"] == "get_system_info":
                    message = json.dumps({
                        "title": "system_info",
                        "subscribers": self.subscribers
                    })
                    Debugger.print(message)
                    self.connection.send(SystemStream.to_bytes(message))

                if data["title"] == "goodbye":
                    self.server_network.abort_received = True
                    break

                if data["title"] == "command":
                    if data["command"] == "should_move":
                        self.received_orders.trucks = data["move"]

                    if data["command"] == "arm_move":
                        self.received_orders.right_arm = data["move"]

                    if data["command"] == "change_speeds":
                        self.received_orders.speeds = data["move"]

            except Exception as e:
                Debugger.RED().print(f"ServerSystemStream: {e}")
                self.server_network.abort_received = True
                break

        Debugger.GREEN().print("Server system stream finished working")

