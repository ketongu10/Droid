from subprocess import Popen
from time import sleep
from RPI.control.main.monitoring.IPhysicalDevice import IPhysicalDevice
from RPI.control.project_settings import UNITY



class PosViewer(IPhysicalDevice):

    def __init__(self):
        pass


    def on_activate_viewer(self, key):
        self.view_process = Popen(UNITY/'ViewPosition.exe')


    def on_deactivate_viewer(self):
        if self.view_process.poll() is None:
            self.view_process.terminate()

    def check_alive_viewer(self):
        return self.view_process.poll() is None


if __name__=="__main__":
    pw = PosViewer()
    print(UNITY/'ViewPosition.exe')
    pw.on_activate_viewer('You are loh')
    sleep(10)
    pw.on_deactivate_viewer()