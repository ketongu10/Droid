import json


def calc_angles_velocities(config, data, is_right):
    arm = config[f"{'right' if is_right else 'left'}_arm"]
    sf = arm['shoulder_forward'].calc_angles(float(data[5]))
    ss = arm['shoulder_side'].calc_angles(float(data[4]))
    es = arm['elbow_side'].calc_angles(float(data[3]))
    ff = arm['forearm_forward'].calc_angles(float(data[2]))
    fs = arm['forearm_side'].calc_angles(float(data[1]))
    h = arm['hand'].calc_angles(float(data[0]))
    return sf, ss, es, ff, fs, h



def make_bytecode_func(k, bias):
    def f(x):
        return k * x + bias

    return f


def read_body_config(path):
    body_coefs_dict = {}
    with open(path, 'r') as f:
        data = json.load(f)

        for key, value in data.items():
            if "arm" in key:
                body_coefs_dict[key] = {}
                for key_, value_ in value.items():
                    body_coefs_dict[key][key_] = ArmElement(**value_)
            else:
                body_coefs_dict[key] = value

    return body_coefs_dict


def update_body_config(config: dict, path):
    to_dump = {}
    for key, value in config.items():
        if "arm" in key:
            to_dump[key] = {}
            for key_, value_ in value.items():
                to_dump[key][key_] = value_.to_dict()
        else:
            to_dump[key] = value

    with open(path, 'w') as f:
        json.dump(to_dump, f)


class ArmElement:

    def __init__(self, k=0.001, bias=0.0, encoder_k=1.0, motor_direction=1):
        self.k: float = k
        self.bias: float = bias
        self.encoder_k: float = encoder_k
        self.motor_direction: int = motor_direction
        self.calc_angles = make_bytecode_func(self.k, self.bias)

    def to_dict(self):
        return {
            "k": self.k,
            "bias": self.bias,
            "encoder_k": self.encoder_k,
            "motor_direction": self.motor_direction
        }


if __name__ == "__main__":
    a= ArmElement()
    print(a.__getattribute__("bias"))
    # conf = read_body_config("C:/Users/ketongu/PycharmProjects/Droid/"
    #                         "RPI/control/resources/body_config.json")
    # print(conf)
    # update_body_config(conf, "C:/Users/ketongu/PycharmProjects/Droid/"
    #                          "RPI/control/resources/body_config2.json")
