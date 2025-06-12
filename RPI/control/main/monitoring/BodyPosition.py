
import matplotlib.pyplot as plt
from multiprocessing.shared_memory import SharedMemory
from multiprocessing import Process
import numpy as np
from time import time
from RPI.control.main.monitoring.AbstractMonitoring import VACharacteristics, AbstractMonitor
from RPI.control.main.monitoring.IPhysicalDevice import IPhysicalDevice
from RPI.control.project_settings import RESOURCES, SHM_CLIENT_SYSSTR_TIME


class Vector3:
    x=0
    y=0
    z=0


class Joint(IPhysicalDevice):
    def __init__(self, side):
        self.angle = AbstractMonitor(100, (0, 1), side=side)
        self.angular_speed = AbstractMonitor(100, (-1, 1), side=side)
        self.rotor_speed = AbstractMonitor(100, (-1, 1), side=side)
        self.VA = VACharacteristics(100, (-16, 16), side=side)

    def get_subscribers(self) -> dict:
        return {"angle": self.angle.last(),
                "angular_speed": self.angular_speed.last(),
                "rotor_speed": self.rotor_speed.last(),
                "VA": self.VA.get_subscribers()}

    def set_subscription_values(self, parameters: dict):
        self.angle.update_buffer(parameters["angle"])
        self.angular_speed.update_buffer(parameters["angular_speed"])
        self.rotor_speed.update_buffer(parameters["rotor_speed"])
        self.VA.set_subscription_values(parameters["VA"])

    def get_info(self) -> tuple:
        return (*self.angle.get_info(), 'angle'), \
               (*self.angular_speed.get_info(), 'angular_speed'), \
               (*self.rotor_speed.get_info(), 'rotor_speed'),\
               (*self.VA.V.get_info(), 'V')




class Trucks(IPhysicalDevice):
    def __init__(self, side):
        self.speed = Vector3()
        self.angular_speed = Vector3()
        self.right_truck_VA = VACharacteristics(100, side=side)
        self.left_truck_VA = VACharacteristics(100, side=side)

    def get_subscribers(self) -> dict:
        return {
            "speed": (self.speed.x, self.speed.y, self.speed.z),
            "angular_speed": (self.angular_speed.x, self.angular_speed.y, self.angular_speed.z),
            "right_truck_VA": self.right_truck_VA.get_subscribers(),
            "left_truck_VA": self.left_truck_VA.get_subscribers()
        }

    def set_subscription_values(self, parameters: dict):
        self.speed = parameters["speed"] #!!!
        self.angular_speed = parameters["angular_speed"] #???
        self.right_truck_VA.set_subscription_values(parameters["right_truck_VA"])
        self.left_truck_VA.set_subscription_values(parameters["left_truck_VA"])


class Arm(IPhysicalDevice):
    def __init__(self, side):
        self.shoulder_forward = Joint(side)  # большой белый мотор толкающий всю руку вперед
        self.shoulder_side = Joint(side)     # редкий мотор поднимающий всю руку в бок
        self.elbow_side = Joint(side)        # стандартный мотор вращающий локоть вдоль своей оси
        self.forearm_forward = Joint(side)   # большой белый мотор сгибающий руку в локте
        self.forearm_side = Joint(side)      # стандартный мотор вращающий предплечье вдоль своей оси
        self.hand = Joint(side)              # стандартный мотор открывающий клешню


class BodyPosition(IPhysicalDevice):
    def __init__(self, side):
        self.right_arm = Arm(side)
        self.left_arm = Arm(side)
        self.trucks = Trucks(side)




