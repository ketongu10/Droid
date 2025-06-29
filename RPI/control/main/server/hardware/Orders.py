from enum import Enum


class Orders:
    trucks: str = "_|_"
    right_arm: str = "______"
    left_arm: str = "______"
    speeds: str = "22"
    # target_pos: str = '_'


class Mode:
    def __init__(self,
                 manual: str=None,
                 voltage: str=None,
                 position: str=None,
                 speed: str=None):
        self.data = {
            'manual': manual,
            'voltage': voltage,
            'position': position,
            'speed': speed,
        }

    def to_floats(self, mode):
        return [float(smth) for smth in self.data[mode].split('|')]

    def from_floats(self, floats: list|tuple, mode):
        self.data[mode] = '|'.join([str(smth) for smth in floats])





class ControlMode(Enum):
    M = "manual"
    P = "position"
    V = "voltage"

    @classmethod
    def get_by_value(cls, value):
        for member in cls:
            if member.value == value:
                print('found')
                return member

        return ControlMode.M


class GeneralOrders:

    def __init__(self):
        self.data = {
            'mode': ControlMode.M.value,
            'trucks': Mode('_|_', '_|_', '_|_', '2'),
            'right_arm': Mode('_|_|_|_|_|_|_',
                             '_|_|_|_|_|_|_',
                             '_|_|_|_|_|_|_',
                             '2'
                             ),
            'left_arm': Mode('_|_|_|_|_|_|_',
                            '_|_|_|_|_|_|_',
                            '_|_|_|_|_|_|_',
                            '2'
                            )
        }

    def serialize(self):
        return {
            'mode': self.data['mode'],
            'trucks': self.data['trucks'].data,
            'right_arm': self.data['right_arm'].data,
            'left_arm': self.data['left_arm'].data
        }

    def deserialize(self, new_data):
        self.data = {
            'mode': new_data['mode'],
            'trucks': Mode(**new_data['trucks']),
            'right_arm': Mode(**new_data['right_arm']),
            'left_arm': Mode(**new_data['left_arm']),
        }


if __name__ == "__main__":
    print(ControlMode.M)
    print({'a':ControlMode.M.value})




















