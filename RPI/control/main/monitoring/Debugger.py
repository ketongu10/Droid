import inspect
from pathlib import Path
from colorama import Fore, Style
import sys

class Debugger:
    subscribers = []
    stdout = []
    DEFAULT_COLOR = Fore.CYAN

    color = DEFAULT_COLOR

    @staticmethod
    def print(*message):
        frame = inspect.currentframe().f_back
        function_name = frame.f_code.co_name
        file_name = Path(frame.f_code.co_filename).name[:-3]
        agent = file_name+"."+function_name
        if agent in Debugger.subscribers:
            for out in Debugger.stdout:
                mess = [str(smth) for smth in message]
                if out is sys.stdout:
                    print(f"{Debugger.color}{agent}:{Style.RESET_ALL} {' '.join(mess)}", file=out)
                else:
                    print(f"{agent}: {' '.join(mess)}", file=out)

        Debugger.color = Debugger.DEFAULT_COLOR

    @staticmethod
    def clr(color):
        Debugger.color = color
        return Debugger

    @staticmethod
    def setup_output(file: Path | str):
        file.parent.mkdir(parents=True, exist_ok=True)
        Debugger.stdout.append(file.open( 'w'))

    @staticmethod
    def setup_stdout():
        Debugger.stdout.append(sys.stdout)

    @staticmethod
    def finalize():
        for out in Debugger.stdout:
            if out is not sys.stdout:
                print(f"From Debugger: closing file", file=out)
                out.close()

    @staticmethod
    def RED():
        Debugger.color = Fore.RED
        return Debugger

    @staticmethod
    def GREEN():
        Debugger.color = Fore.GREEN
        return Debugger

    @staticmethod
    def BLUE():
        Debugger.color = Fore.BLUE
        return Debugger

    @staticmethod
    def CYAN():
        Debugger.color = Fore.CYAN
        return Debugger

    @staticmethod
    def ORANGE():
        Debugger.color = Fore.LIGHTRED_EX
        return Debugger

