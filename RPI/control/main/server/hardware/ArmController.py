import math
import os.path
from enum import Enum

import numpy as np

from RPI.control.main.monitoring.Debugger import Debugger
from RPI.control.main.monitoring.SystemMonitoring import SystemMonitoring
from RPI.control.main.server.hardware.Interfaces.IDevice import IDevice
from RPI.control.main.server.hardware.Interfaces.IExecuteOrders import IExecuteOrders
from RPI.control.main.server.hardware.Interfaces.IUseI2C import IUseI2C
from RPI.control.main.server.hardware.Orders import Orders, GeneralOrders, ControlMode
import serial

from RPI.control.main.server.hardware.iohelper import calc_angles_velocities, calc_speeds
from RPI.control.main.server.hardware.motor_filter import MotorFilter


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

    @staticmethod
    def FROM_SIGN(direction):
        if direction>0:
            return Motions.UP
        elif direction<0:
            return Motions.DOWN
        return Motions.STOP

    @staticmethod
    def TO_SIGN(motion):
        if motion == Motions.UP:
            return 1
        elif motion == Motions.DOWN:
            return -1
        return 0


class MotorBuffer:
    def __init__(self, motion, pwm_level):
        self.motion_adr = motion
        self.pwm_level_adr = pwm_level


class ArmController(IUseI2C, IExecuteOrders, IDevice):
    motor_table = {
        "shoulder_forward": MotorBuffer(0x08, 0x09), #MotorBuffer(0x00, 0x01),
        "shoulder_side": MotorBuffer(0x0a, 0x0b), #MotorBuffer(0x02, 0x03),
        "elbow_side": MotorBuffer(0x06, 0x07), #MotorBuffer(0x04, 0x05),
        "forearm_forward": MotorBuffer(0x04, 0x05), #MotorBuffer(0x06, 0x07),
        "forearm_side": MotorBuffer(0x00, 0x01), #MotorBuffer(0x08, 0x09),
        "hand": MotorBuffer(0x02, 0x03), #MotorBuffer(0x0a, 0x0b),
    }
    SPEEDS = [0, 86, 127, 200, 255]


    def __init__(self,  bus, adr, hw_controller, is_right_arm=True):
        super().__init__(bus, adr[0])
        self.hw_controller = hw_controller
        self.encoder_desc_path = adr[1]
        self.encoder_desc = None
        self.mode = "______"
        self.control_mode = ControlMode.M.value

        self.right_arm = is_right_arm
        self.arm_key = f"{'right' if self.right_arm else 'left'}_arm"
        self.arm_speed = 2
        self.target_pos = {
            # "shoulder_forward": -1,
            # "shoulder_side": -1,
            # "elbow_side": -1,
            # "forearm_forward": -1,
            # "forearm_side": -1,
            "hand": 0.5,
        }
        self.motor_filters = {}
        # for key in self.target_pos.keys():
        #     self.motor_filters[key] = MotorFilter(size=7, sigma=2)
        for key in ArmController.motor_table.keys():
            self.motor_filters[key] = MotorFilter(size=7, sigma=2)


    def is_available(self):

        motion_is_ok = False
        encoder_is_ok = False

        try:
            self.bus.read_byte_data(self.malina_adr, IUseI2C.DEFAULT_CHECK_POINT)
            motion_is_ok = True
        except Exception as e:
            Debugger.RED().print(f'{"right" if self.right_arm else "left"} '
                                 f'arm motion malina {self.malina_adr} is not available')

        try:
            self.encoder_desc = serial.Serial(self.encoder_desc_path, 2000000, timeout=1)
            encoder_is_ok = True
        except Exception as e:
            Debugger.RED().print(f'{"right" if self.right_arm else "left"} '
                                 f'arm encoder malina {self.encoder_desc} is not available')

        return motion_is_ok and encoder_is_ok

    def move_i_motor(self, motor_key, motion: Motions, pwm_level):

        actual_action = self.motor_filters[motor_key](Motions.TO_SIGN(motion)*pwm_level)
        actual_pwm, actual_motion = int(abs(actual_action))%255, Motions.FROM_SIGN(actual_action)

        self.bus.write_byte_data(self.malina_adr, ArmController.motor_table[motor_key].motion_adr, actual_motion.value)
        self.bus.write_byte_data(self.malina_adr, ArmController.motor_table[motor_key].pwm_level_adr, actual_pwm)

        self.hw_controller.system_monitoring.body.\
                        __getattribute__(self.arm_key).\
                        __getattribute__(motor_key).\
                        VA.V.update_buffer(16 * actual_action / 255)

    def execute_orders_old(self, orders: Orders) -> None:
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

            # """
            #     change target pos
            # """
            # if orders.target_pos != '_':
            #     self.target_pos["hand"] = float(orders.target_pos)

            """
                MOVE MOTORS
            """
            directives = orders.right_arm if self.right_arm else orders.left_arm

            should_change = False
            # check whether directives changed
            for i, motor_key in enumerate(ArmController.motor_table.keys()):
                self.move_i_motor(motor_key, Motions.get_by_code(directives[i]), ArmController.SPEEDS[self.arm_speed])
                if self.mode[i] != directives[i]:
                    # setting up new directives
                    should_change = True

                    if should_change:
                        if motor_key in self.target_pos.keys():
                            self.target_pos[motor_key] = self.hw_controller.system_monitoring.body. \
                                __getattribute__(self.arm_key). \
                                __getattribute__(motor_key).angle.last_values[-1]
            if should_change:
                self.mode = directives
                # for key in self.target_pos.keys():
                #     arm_key = f"{'right' if self.right_arm else 'left'}_arm"
                #     self.target_pos[key] = self.hw_controller.system_monitoring.body.\
                #         __getattribute__(arm_key).\
                #         __getattribute__(key).angle



    def execute_orders(self, orders: GeneralOrders) -> None:
        if orders:

            control_mode = orders.data['mode']
            self.control_mode = control_mode
            if control_mode == ControlMode.M.value:

                sp_ar = int(orders.data[self.arm_key].data['speed'])
                if sp_ar > 4 or sp_ar < 0:
                    Debugger.ORANGE().print(f"THERE IS NO SUCH SPEED {sp_ar}")
                else:
                    self.arm_speed = sp_ar
                    directives = orders.data[self.arm_key].data[control_mode].replace('|', '')

                    self.mode = directives

                    for i, motor_key in enumerate(ArmController.motor_table.keys()):
                        self.move_i_motor(motor_key, Motions.get_by_code(directives[i]), ArmController.SPEEDS[self.arm_speed])

            elif control_mode == ControlMode.P.value:

                sp_ar = int(orders.data[self.arm_key].data['speed'])
                if sp_ar > 4 or sp_ar < 0:
                    Debugger.ORANGE().print(f"THERE IS NO SUCH SPEED {sp_ar}")
                else:
                    self.arm_speed = sp_ar
                    self.mode = '______'
                    for i, motor_key in enumerate(ArmController.motor_table.keys()):
                        if motor_key in self.target_pos.keys():
                            self.target_pos[motor_key] = orders.data[self.arm_key].to_floats(control_mode)

            else:
                self.mode = '______'








    def get_angle_by_bufpos(self, bufpos):
        ret = (self.bus.read_byte_data(self.encoder_desc, bufpos - 1) * 255 +
               self.bus.read_byte_data(self.encoder_desc, bufpos)) % 360

        return ret


    def parse_serial(self):
        last_line = ""
        while self.encoder_desc.in_waiting > 0:
            line = self.encoder_desc.readline().decode('utf-8').strip()
            if line:  # Игнорируем пустые строки
                last_line = line
        data = last_line.split('_') if last_line else None
        if data is not None:
            data = data[1:7], calc_angles_velocities(self.hw_controller.body_config, data[7:13], self.right_arm)

        return data


    def carry_out_measurements(self, subscribers: SystemMonitoring) -> None:
        data = self.parse_serial()
        if data:
            rotor_speeds, (sf, ss, es, ff, fs, h) = data
            if self.right_arm:
                subscribers.body.right_arm.shoulder_forward.angle.update_buffer(sf)
                subscribers.body.right_arm.shoulder_side.angle.update_buffer(ss)
                subscribers.body.right_arm.elbow_side.angle.update_buffer(es)
                subscribers.body.right_arm.forearm_forward.angle.update_buffer(ff)
                subscribers.body.right_arm.forearm_side.angle.update_buffer(fs)
                subscribers.body.right_arm.hand.angle.update_buffer(h)

                subscribers.body.right_arm.hand.angular_speed.update_buffer(
                    calc_speeds(subscribers.body.right_arm.hand.angle.last_values,
                                subscribers.time.last_values)
                )
                subscribers.body.right_arm.hand.rotor_angle.update_buffer(
                    (float(rotor_speeds[0])-1000)
                )
                subscribers.body.right_arm.hand.rotor_speed.update_buffer(
                    calc_speeds(subscribers.body.right_arm.hand.rotor_angle.last_values,
                                subscribers.time.last_values)/200
                )
            else:
                subscribers.body.left_arm.shoulder_forward.angle.update_buffer(sf)
                subscribers.body.left_arm.shoulder_side.angle.update_buffer(ss)
                subscribers.body.left_arm.elbow_side.angle.update_buffer(es)
                subscribers.body.left_arm.forearm_forward.angle.update_buffer(ff)
                subscribers.body.left_arm.forearm_side.angle.update_buffer(fs)
                subscribers.body.left_arm.hand.angle.update_buffer(h)

        if self.control_mode == ControlMode.P.value:
            self.hold_last_pos(subscribers)


    def hold_last_pos(self, subscribers: SystemMonitoring):

        min_val = 0.01
        if self.mode == "______":
            arm = subscribers.body.__getattribute__(self.arm_key)
            arm_config = self.hw_controller.body_config[self.arm_key]
            for key in self.target_pos.keys():
                dif = arm.__getattribute__(key).angle.last_values[-1] - self.target_pos[key]
                pwm = int(ArmController.SPEEDS[self.arm_speed] * self.clip(abs(dif-min_val)/min_val/2, 0, 1))
                direction = dif * arm_config[key].motor_direction
                direction = Motions.FROM_SIGN(direction)
                print(dif, key)
                if abs(dif) < min_val:
                    self.move_i_motor(key, Motions.STOP, 0)
                else:
                    self.move_i_motor(key, direction, pwm)

    def clip(self, val, mn, mx):
        if val < mn:
            return mn
        elif val > mx:
            return mx
        return val

    def finalize(self):
        try:
            for key in ArmController.motor_table.keys():
                self.bus.write_byte_data(self.malina_adr, ArmController.motor_table[key].motion_adr, Motions.STOP.value)

            self.encoder_desc.close()
        except: pass


