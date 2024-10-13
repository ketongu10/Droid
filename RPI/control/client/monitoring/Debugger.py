import inspect


class Debugger:
    subscribers = []
    stdout = None

    @staticmethod
    def print(message):
        frame = inspect.currentframe().f_back
        function_name = frame.f_code.co_name
        context = frame.f_back.f_locals
        if context.get('Debugger'):
            class_name = list(frame.f_back.f_locals.keys())[-1]
        else:
            class_name = list(frame.f_back.f_back.f_locals.keys())[-1]
        agent = class_name+'.'+function_name
        if agent in Debugger.subscribers:
            if Debugger.stdout:
                print(f"{agent}: {message}", file=Debugger.stdout)
            else:
                print(f"{agent}: {message}")

    @staticmethod
    def setup_stdout(file):
        Debugger.stdout = open(file, 'w')

    @staticmethod
    def finalize():
        if Debugger.stdout:
            print(f"From Debugger: closing file", file=Debugger.stdout)
            Debugger.stdout.close()




