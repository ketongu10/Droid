from time import time


class LazyMonitoring:
    last_value = 0
    average_value = 0
    num_values = 0

    def add_value(self, value):
        self.last_value = value
        self.num_values += 1
        self.average_value = (self.average_value*self.num_values+self.last_value)/self.num_values

    def __str__(self):
        return f"{self.last_value:.02f}"

    def dump(self, shift=10):
        return f"last_value: {self.last_value:.02f}\n" \
               f"{' '*shift} average_value: {self.average_value:.02f}\n" \
               f"{' '*shift} num_values: {self.num_values:.02f}"


class Profiler:
    subscribers: dict[str, LazyMonitoring] = {}

    @staticmethod
    def register(agent_name):
        Profiler.subscribers[agent_name] = LazyMonitoring()


        def decorator(function):
            def wrapper(*args, **kwargs):
                t0 = time()
                result = function(*args, **kwargs)
                Profiler.subscribers[agent_name].add_value((time()-t0)*1000)
                return result
            return wrapper
        return decorator

    @staticmethod
    def profile(message: dict):
        for key, value in message.items():
            Profiler.subscribers[key].add_value(value)

    @staticmethod
    def dump(filename, full_info=False):
        with open(filename, 'w') as f:
            for key, value in Profiler.subscribers.items():
                if full_info:
                    print(f"{key}: {value.dump(len(key)+2)}", file=f)
                else:
                    print(f"{key}: {value.last_value:.02f}", file=f)

