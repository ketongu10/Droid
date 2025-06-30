import json
import traceback
from subprocess import Popen
from time import sleep

from RPI.control.main.monitoring.Debugger import Debugger
from RPI.control.main.monitoring.IPhysicalDevice import IPhysicalDevice
from RPI.control.main.monitoring.SystemMonitoring import SystemMonitoring
from RPI.control.project_settings import UNITY



class PosViewer(IPhysicalDevice):

    def __init__(self, system_monitoring=None):
        self.sys_mon = system_monitoring
        if system_monitoring is None:
            Debugger.ORANGE().print("WARNING: empty system_monitoring!!!")

        self.unity_translation_config = {}
        with open(UNITY/'translation_config.json', 'r') as f:
            data = json.load(f)
            for key, value in data["Bones"].items():
                self.unity_translation_config[key] = BoneTranslation(**value)
                self.unity_translation_config[key].parse_reg_name(self.sys_mon)



    def on_activate_viewer(self, key):
        self.view_process = Popen(UNITY/'ViewPosition.exe')


    def on_deactivate_viewer(self):
        if self.view_process.poll() is None:
            self.view_process.terminate()

    def check_alive_viewer(self):
        return self.view_process.poll() is None

    def update_viewer(self):
        data = {}
        for key, bone in self.unity_translation_config.items():
            data[key] = bone.recalculate()
        try:
            with open(UNITY/'ViewPosition_Data/StreamingAssets/transfered_pos_in.json', 'w+') as f:
                json.dump({'angles': data, 'allowDump': True}, f)
        except PermissionError:
            print('POSOSAL')




class BoneTranslation:


    def __init__(self, reg_name='loh', k=1.0, bias=0.0):
        self.reg_name = reg_name
        self.k = k
        self.bias = bias
        self.class_link = None
        self.attr = None

    def parse_reg_name(self, system_monitoring):
        if system_monitoring is not None:
            now_link = system_monitoring
            attrs = self.reg_name.split('/')
            for attr in attrs[:-1]:
                now_link = getattr(now_link, attr)
            self.class_link = now_link
            self.attr = attrs[-1]

    def recalculate(self):
        return getattr(self.class_link, self.attr).last_values[-1] * self.k + self.bias









if __name__=="__main__":

    sysmon = SystemMonitoring()
    pw = PosViewer(sysmon)
    print(pw.unity_translation_config["Bone 1"].recalculate())
    sysmon.body.right_arm.shoulder_forward.angle+=1
    print(pw.unity_translation_config["Bone 1"].recalculate())
    print(repr(pw.unity_translation_config))
    # print(UNITY/'ViewPosition.exe')
    # pw.on_activate_viewer('You are loh')
    # sleep(10)
    # pw.on_deactivate_viewer()