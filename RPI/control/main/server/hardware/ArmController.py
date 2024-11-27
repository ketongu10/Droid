from enum import Enum

from RPI.control.main.monitoring.Debugger import Debugger
from RPI.control.main.server.hardware.Interfaces.IDevice import IDevice
from RPI.control.main.server.hardware.Interfaces.IExecuteOrders import IExecuteOrders
from RPI.control.main.server.hardware.Interfaces.IUseI2C import IUseI2C
from RPI.control.main.server.hardware.Orders import Orders


class Motions(Enum):
    STOP = 0x00
    UP = 0x01
    DOWN = 0x02

    @staticmethod
    def get_by_code(s: str):
        if s == '_':
            return Motions.STOP
        elif s == 'r':
            return Motions.UP
        elif s == 'l':
            return Motions.DOWN
        else:
            print(f"!!!!!!!!!!!  UNEXPECTED MOTION `{s}`  !!!!!!!!!!!")
            return Motions.STOP


class MotorBuffer:
    def __init__(self, motion, pwm_level):
        self.motion_adr = motion
        self.pwm_level_adr = pwm_level


class ArmController(IUseI2C, IExecuteOrders, IDevice):
    motor_table = {
        0: MotorBuffer(0x00, 0x01),
        1: MotorBuffer(0x02, 0x03),
        2: MotorBuffer(0x04, 0x05),
        3: MotorBuffer(0x06, 0x07),
        4: MotorBuffer(0x08, 0x09),
        5: MotorBuffer(0x0a, 0x0b),
    }
    SPEEDS = [0, 86, 127, 200, 255]

    def __init__(self,  bus, adr, is_right_arm=True):
        super().__init__(bus, adr)
        self.mode = "______"
        self.right_arm = is_right_arm
        self.arm_speed = 2

    def move_i_motor(self, i, motion: Motions, pwm_level):
        self.bus.write_byte_data(self.malina_adr, ArmController.motor_table[i].motion_adr, motion.value)
        self.bus.write_byte_data(self.malina_adr, ArmController.motor_table[i].pwm_level_adr, pwm_level)
        #rec = self.bus.read_byte_data(self.malina_adr, ArmController.motor_table[i].motion_adr)

    def execute_orders(self, orders: Orders) -> None:
        if orders:
            """
                CHANGING SPEED
            """
            speeds = orders.speeds
            sp_tr, sp_ar = int(speeds[0]), int(speeds[1])
            if sp_ar > 4 or sp_ar < 0:
                Debugger.ORANGE().print(f"THERE IS NO SUCH SPEED {speeds}")
            else:
                self.arm_speed = sp_ar

            """
                MOVE MOTORS
            """
            directives = orders.right_arm if self.right_arm else orders.left_arm

            should_change = False
            # check whether directives changed
            for i in range(len(self.mode)):
                if self.mode[i] != directives[i]:
                    # setting up new directives
                    should_change = True
                    self.move_i_motor(i, Motions.get_by_code(directives[i]), ArmController.SPEEDS[self.arm_speed])
            if should_change:
                self.mode = directives

    def finalize(self):
        for i in range(6):
            self.bus.write_byte_data(self.malina_adr, ArmController.motor_table[i].motion_adr, Motions.STOP.value)


