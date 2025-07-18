from threading import Thread

import numpy as np
from time import time
from RPI.control.main.monitoring.Debugger import Debugger
from RPI.control.main.monitoring.Profiler import Profiler
from RPI.control.main.monitoring.SystemMonitoring import SystemMonitoring
from RPI.control.main.network.AbstractStream import AbstractStream
from RPI.control.main.server.hardware.Interfaces.IDevice import IDevice
from RPI.control.main.server.hardware.Interfaces.IExecuteOrders import IExecuteOrders
from RPI.control.main.server.hardware.Interfaces.IUseI2C import IUseI2C
from RPI.control.main.server.hardware.Orders import Orders
from RPI.control.main.server.hardware.iohelper import read_body_config
from RPI.control.project_settings import RESOURCES


class HWController(AbstractStream):

    RIGHT_ARM_MALINA_ADR = 0x17, '/dev/ttyUSB0'
    LEFT_ARM_MALINA_ADR = 0x18, '/dev/ttyUSB0'

    ACCUMULATOR_ADR = 0x17

    def __init__(self, cfg, system_monitoring: SystemMonitoring, fps):
        self.dt = 1/fps
        self.camera_is_available = False
        self.trucks_are_available = False
        self.i2c_is_available = False
        self.right_arm_is_available = False
        self.left_arm_is_available = False
        self.accumulator_is_available = False

        self.system_monitoring = system_monitoring
        self.orders: Orders | None = None
        self.working_devices = []

        self.body_config = read_body_config(RESOURCES/"body_config.json")

        self.working = False
        self.hw_thread = Thread(target=self.execute_orders)
        if cfg["device"] == "RPI":
            try:
                from RPI.control.main.server.hardware.CameraController import CameraController
                self.camera = CameraController(cfg)
                self.camera_is_available = True
                self.working_devices.append(self.camera)
                Debugger.GREEN().print("CAMERA IS WORKING")
            except Exception as e:
                Debugger.RED().print(e)

            try:
                from RPI.control.main.server.hardware.TrucksController import TrucksController
                self.trucks = TrucksController()
                self.trucks_are_available = True
                if self.trucks_are_available:
                    self.working_devices.append(self.trucks)
                    Debugger.GREEN().print("TRUCKS ARE WORKING")
            except Exception as e:
                Debugger.RED().print(e)

            try:
                from RPI.control.main.server.hardware.I2CBus import I2CBus
                self.i2c_bus = I2CBus(1)
                self.i2c_is_available = True
                if self.i2c_is_available:
                    self.working_devices.append(self.i2c_bus)
                    Debugger.GREEN().print("I2C BUS FOUND")
            except Exception as e:
                Debugger.RED().print(e)

            if self.i2c_is_available:
                try:
                    from RPI.control.main.server.hardware.ArmController import ArmController
                    self.right_arm = ArmController(self.i2c_bus, HWController.RIGHT_ARM_MALINA_ADR, self)
                    self.right_arm_is_available = self.right_arm.is_available()
                    if self.right_arm_is_available:
                        self.working_devices.append(self.right_arm)
                        Debugger.GREEN().print("RIGHT ARM CONTROLLER IS READY")

                    self.left_arm = ArmController(self.i2c_bus, HWController.LEFT_ARM_MALINA_ADR, self, is_right_arm=False)
                    self.left_arm_is_available = self.left_arm.is_available()
                    if self.left_arm_is_available:
                        self.working_devices.append(self.left_arm)
                        Debugger.GREEN().print("LEFT ARM CONTROLLER IS READY")
                except Exception as e:
                    Debugger.RED().print(e)

                try:
                    from RPI.control.main.server.hardware.AccumulatorController import AccumulatorController
                    self.accumulator = AccumulatorController(self.i2c_bus, HWController.ACCUMULATOR_ADR)
                    self.accumulator_is_available = self.accumulator.is_available()
                    if self.accumulator_is_available:
                        self.working_devices.append(self.accumulator)
                except Exception as e:
                    Debugger.RED().print(e)

        if self.working_devices or True:

            self.working = True
            self.hw_thread.start()

    def execute_orders(self):
        while self.working:
            HWController.maintain_fps(self._execute_orders, self.dt)

    @Profiler.register("execute_orders")
    def _execute_orders(self):

        for device in self.working_devices:
            if isinstance(device, IExecuteOrders):
                device.carry_out_measurements(self.system_monitoring)
                device.execute_orders(self.orders)

        self.system_monitoring.time.update_buffer(time()-self.system_monitoring.initial_time)
        self.system_monitoring.update_subscribers()

    def finalize(self):
        self.working = False
        self.hw_thread.join()
        for device in self.working_devices[::-1]:
            if isinstance(device, IDevice):
                device.finalize()
        Debugger.GREEN().print("HW thread finished working")
