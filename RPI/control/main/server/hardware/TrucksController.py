import RPi.GPIO as IO
from time import sleep

from RPI.control.main.server.hardware.Interfaces.IDevice import IDevice
from RPI.control.main.server.hardware.Interfaces.IExecuteOrders import IExecuteOrders
from RPI.control.main.server.hardware.Orders import Orders, GeneralOrders


class TrucksController(IExecuteOrders, IDevice):
    SPEEDS = [0, 86, 127, 200, 255]
    INPUT_CONVERTER = {
        'l|_': "turn_left",
        'r|_': "turn_right",
        '_|u': "forward",
        '_|d': "backward",
        'l|u': "forward_left",
        'r|u': "forward_right",
        'l|d': "backward_left",
        'r|d': "backward_right",
        '_|_': "stop_move"
    }

    def __init__(self):
        self.prepareIO()
        self.pr = IO.PWM(12, 100)
        self.pl = IO.PWM(13, 100)
        self.mode = "stop_move"
        self.trucks_speed = 2
        self.change_mode = {
            "forward": self.move_forward,
            "backward": self.move_backward,
            "turn_right": self.turn_right,
            "turn_left": self.turn_left,
            "stop_move": self.stop_move,
            "forward_right": self.forward_right,
            "forward_left": self.forward_left,
            "backward_right": self.backward_right,
            "backward_left": self.backward_left
        }

    def execute_orders(self, orders: GeneralOrders) -> None:
        if orders:
            """
                CHANGING SPEED
            """
            control_mode = orders.data['mode']
            sp_tr = int(orders.data['trucks'].data['speed'])
            if sp_tr > 4 or sp_tr < 0:
                print(f"THERE IS NO SUCH SPEED {sp_tr}")
            else:
                self.trucks_speed = sp_tr

            """
                MOVE MOTORS
            """
            new_mode = TrucksController.INPUT_CONVERTER.get(orders.data['trucks'].data[control_mode])
            if not new_mode:
                new_mode = "stop_move"

            if new_mode != self.mode:
                self.stop_move()
                self.change_mode[new_mode]()
                self.mode = new_mode

    def prepareIO(self):
        IO.setwarnings(False)
        IO.setmode(IO.BCM)

        IO.setup(5, IO.OUT)  # left mototr move forward
        IO.setup(6, IO.OUT)  # left mototr turn backward
        IO.setup(13, IO.OUT)  # left mototr pwm

        IO.setup(16, IO.OUT)  # right mototr move backrward
        IO.setup(20, IO.OUT)  # right mototr move forward
        IO.setup(12, IO.OUT)  # right mototr pwm

        IO.setup(19, IO.OUT)  # driver turn on

        IO.output(19, IO.HIGH)
        IO.output(16, IO.LOW)
        IO.output(20, IO.LOW)
        IO.output(5, IO.LOW)
        IO.output(6, IO.LOW)

    def move_forward(self):
        IO.output(20, IO.HIGH)
        IO.output(5, IO.HIGH)
        self.pr.start(100 * TrucksController.SPEEDS[self.trucks_speed] / 255)
        self.pl.start(100 * TrucksController.SPEEDS[self.trucks_speed] / 255)

    def move_backward(self):
        IO.output(16, IO.HIGH)
        IO.output(6, IO.HIGH)
        self.pr.start(100 * TrucksController.SPEEDS[self.trucks_speed] / 255)
        self.pl.start(100 * TrucksController.SPEEDS[self.trucks_speed] / 255)

    def turn_right(self):
        IO.output(16, IO.HIGH)
        IO.output(5, IO.HIGH)
        self.pr.start(100 * TrucksController.SPEEDS[self.trucks_speed] / 255)
        self.pl.start(100 * TrucksController.SPEEDS[self.trucks_speed] / 255)

    def turn_left(self):
        IO.output(20, IO.HIGH)
        IO.output(6, IO.HIGH)
        self.pr.start(100 * TrucksController.SPEEDS[self.trucks_speed] / 255)
        self.pl.start(100 * TrucksController.SPEEDS[self.trucks_speed] / 255)

    def forward_right(self):
        IO.output(20, IO.HIGH)
        IO.output(5, IO.HIGH)
        self.pr.start(40 * TrucksController.SPEEDS[self.trucks_speed] / 255)
        self.pl.start(100 * TrucksController.SPEEDS[self.trucks_speed] / 255)

    def forward_left(self):
        IO.output(20, IO.HIGH)
        IO.output(5, IO.HIGH)
        self.pr.start(100 * TrucksController.SPEEDS[self.trucks_speed] / 255)
        self.pl.start(40 * TrucksController.SPEEDS[self.trucks_speed] / 255)

    def backward_right(self):
        IO.output(16, IO.HIGH)
        IO.output(6, IO.HIGH)
        self.pr.start(40 * TrucksController.SPEEDS[self.trucks_speed] / 255)
        self.pl.start(100 * TrucksController.SPEEDS[self.trucks_speed] / 255)

    def backward_left(self):
        IO.output(16, IO.HIGH)
        IO.output(6, IO.HIGH)
        self.pr.start(100 * TrucksController.SPEEDS[self.trucks_speed] / 255)
        self.pl.start(40 * TrucksController.SPEEDS[self.trucks_speed] / 255)

    def stop_move(self):
        IO.output(16, IO.LOW)
        IO.output(5, IO.LOW)
        IO.output(20, IO.LOW)
        IO.output(6, IO.LOW)
        self.pr.stop()
        self.pl.stop()

    def finalize(self):
        self.stop_move()
        IO.cleanup()
