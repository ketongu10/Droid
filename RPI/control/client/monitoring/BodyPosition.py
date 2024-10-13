from RPI.control.client.monitoring.AbstractMonitoring import VACharacteristics
from RPI.control.client.monitoring.IPhysicalDevice import IPhysicalDevice


class Vector3:
    x=0
    y=0
    z=0


class Joint(IPhysicalDevice):
    def __init__(self):
        self.angle = 0
        self.angular_speed = 0
        self.VA = VACharacteristics(100)


class Trucks(IPhysicalDevice):
    def __init__(self):
        self.speed = Vector3()
        self.angular_speed = Vector3()
        self.right_truck_VA = VACharacteristics(100)
        self.left_truck_VA = VACharacteristics(100)

    def get_subscribers(self) -> dict:
        return {
            "speed": (self.speed.x, self.speed.y, self.speed.z),
            "angular_speed": (self.angular_speed.x, self.angular_speed.y, self.angular_speed.z),
            "right_truck_VA": self.right_truck_VA.get_subscribers(),
            "left_truck_VA": self.left_truck_VA.get_subscribers()
        }

    def set_subscription_values(self, parameters: dict):
        self.speed = parameters["speed"]
        self.angular_speed = parameters["angular_speed"]
        self.right_truck_VA.set_subscription_values(parameters["right_truck_VA"])
        self.left_truck_VA.set_subscription_values(parameters["left_truck_VA"])


class Arm(IPhysicalDevice):
    def __init__(self):
        self.shoulder_forward = Joint()  # большой белый мотор толкающий всю руку впере
        self.shoulder_side = Joint()     # редкий мотор поднимающий всю руку в бок
        self.elbow_side = Joint()        # стандартный мотор вращающий локоть вдоль своей оси
        self.forearm_forward = Joint()   # большой мотор сгибающий руку в локте
        self.forearm_side = Joint()      # стандартный мотор вращающий предплечье вдоль своей оси
        self.hand = Joint()              # стандартный мотор открывающий клешню


class BodyPosition(IPhysicalDevice):
    def __init__(self):
        self.right_arm = Arm()
        self.left_arm = Arm()
        self.trucks = Trucks()




