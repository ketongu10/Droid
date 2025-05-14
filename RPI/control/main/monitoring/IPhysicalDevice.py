from multiprocessing import Process

class IPhysicalDevice:


    view_process = None

    def set_subscription_values(self, parameters: dict):
        for key, value in parameters.items():
            if isinstance(self.__getattribute__(key), IPhysicalDevice):
                self.__getattribute__(key).set_subscription_values(value)
                # self.__setattr__(key, self.__getattribute__(key).set_subscription_values(value))
            else:
                self.__setattr__(key, value)

    def get_subscribers(self) -> dict:
        ret = {}
        for key, value in self.__dict__.items():
            if isinstance(value, IPhysicalDevice):
                ret[key] = value.get_subscribers()
            else:
                ret[key] = value
        return ret

    def get_info(self) -> tuple: ...

    def on_activate_viewer(self, key): ...

    def on_deactivate_viewer(self): ...

    def check_alive_viewer(self):
        """RETURNS True if alive"""
        return self.view_process.is_alive()