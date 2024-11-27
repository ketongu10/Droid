import sys

import pygame
import numpy as np

from RPI.control.main.monitoring.Profiler import Profiler
from RPI.control.main.network.Side import Side
from RPI.control.main.network.client.ClientNetwork import ClientNetwork
from RPI.control.main.monitoring.SystemMonitoring import SystemMonitoring
from inputoutput.InputHandler import InputHandler
from inputoutput.ClientMainScreen import ClientMainScreen
from RPI.control.main.monitoring.Debugger import Debugger
from RPI.control.main.monitoring.InitSubscribers import init_subscribers
from RPI.control.project_settings import RESOURCES
from time import time
import yaml


class Client:
    FPS = 1
    system_monitoring: SystemMonitoring | None
    input_handler: InputHandler | None
    network: ClientNetwork | None
    clock = None

    @staticmethod
    def initial_setup():
        with open(RESOURCES/'config.yml', 'r') as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
        pygame.init()

        sys.setswitchinterval(0.005)
        init_subscribers(side=Side.Client)
        Client.system_monitoring = SystemMonitoring()
        main_menu = ClientMainScreen.init_screen(Client.system_monitoring)
        Client.input_handler = InputHandler(main_menu)
        Client.network = ClientNetwork(cfg, Client.system_monitoring.get_subscribers(), Client.FPS)
        Client.clock = pygame.time.Clock()


    @staticmethod
    def handle_input() -> dict:
        ret = Client.input_handler.get_control_input()
        if ret["status"] == "Quit":
            Client.abort_connections()
            pygame.quit()
            sys.exit()

        elif ret["status"] == "Successfully":
            return ret
        else:
            Debugger.print(f"Unexpected input return {ret}")
            Client.abort_connections()


    @staticmethod
    def abort_connections():
        Client.network.abort_connection()


    @staticmethod
    def update_data_received_from_server():

        Client.system_monitoring.set_subscription_values(Client.network.system_stream.received_data["subscribers"])

    @staticmethod
    def send_commands_to_server(control_inputs: dict):
        Client.network.send_commands_to_server(control_inputs)

    @staticmethod
    def render_screen(tick):
        ClientMainScreen.render_screen(Client, tick)




def main():
    Client.initial_setup()
    while True:
        tick = Client.clock.tick(Client.FPS) / 1000.0
        input_data = Client.handle_input()
        Client.send_commands_to_server(input_data)
        Client.update_data_received_from_server()
        Client.render_screen(tick)
        Profiler.dump(RESOURCES / "prof_client.txt", full_info=True)
        if Client.network.abort_received:
            Client.network.abort_server_side()
            break




if __name__ == "__main__":
    main()
