import pygame
import numpy as np
from network.Network import Network
from monitoring.SystemMonitoring import SystemMonitoring
from inputoutput.InputHandler import InputHandler
from inputoutput.ClientMainScreen import ClientMainScreen
from RPI.control.client.monitoring.Debugger import Debugger
from RPI.control.client.monitoring.InitSubscribers import init_subscribers
from time import time
import yaml


class Client:

    network: Network | None
    system_monitoring: SystemMonitoring | None
    clock = None

    @staticmethod
    def initial_setup():
        with open('./config.yml', 'r') as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
        pygame.init()
        Client.system_monitoring = SystemMonitoring()
        Client.network = Network(cfg, Client.system_monitoring.get_subscribers())
        Client.clock = pygame.time.Clock()
        ClientMainScreen.init_screen()
        init_subscribers()

    @staticmethod
    def handle_input() -> dict:
        ret = InputHandler.get_control_input()
        if ret["status"] == "Quit":
            Client.abort_connections()
            exit()
        elif ret["status"] == "Successfully":
            return ret
        else:
            Debugger.print(f"Unexpected input return {ret}")
            Client.abort_connections()
            exit()

    @staticmethod
    def abort_connections():
        Client.network.abort_connection()

    @staticmethod
    def update_data_received_from_server():
        Client.system_monitoring.set_subscription_values(Client.network.system_stream.received_data)

    @staticmethod
    def send_commands_to_server(control_inputs: dict):
        Client.network.send_commands_to_server(control_inputs)

    @staticmethod
    def render_screen():
        ClientMainScreen.render_screen()




def main():
    Client.initial_setup()
    while True:
        input_data = Client.handle_input()
        Client.send_commands_to_server(input_data)
        Client.update_data_received_from_server()
        Client.render_screen()
        Client.clock.tick(60)



if __name__ == "__main__":
    main()