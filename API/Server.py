import keyboard
from API.WorldProxy import WorldProxy
from API.Droids.DroidLinReg import DroidLinReg
from API.Droids.DroidBase import DroidBase
from Worlds.Snake import C
import time


class Server:
    """Server used to organise Droid and World communication"""
    def __init__(self, snake):
        self.world = WorldProxy(snake)
        self.droid = DroidLinReg(self.world)
        self.guided = True
        self.is_active = True

    def tick(self, t):
        ticks = 1/self.world.fps - t
        if ticks < 0:
            try:
                print(f"WARNING!!!! DROID'S FPS IS TOO LOW!!!! \n FPS IS: {1/t:.0f}")
            except:
                pass

        time.sleep(ticks if ticks > 0 else 0)

    def change_control(self):
        if self.guided:
            print("DROID: Master control activated")
            self.world.snake.snake_speed = C.snake_speed_slow
            self.world.fps = C.snake_speed_slow
            self.guided = False
        else:
            print("DROID: Master control deactivated")
            self.guided = True
            self.world.snake.snake_speed = C.snake_speed_fast
            self.world.fps = C.snake_speed_fast
            #self.droid.analyse()

    def deactivate(self):
        print("DROID: Droid is deactivated")
        self.is_active = False
        self.guided = False

    def loop(self):
        self.guided = True
        self.is_active = True
        while self.is_active:
            t = time.time()
            if not self.world.snake.game_close:
                if self.guided:
                    pic = self.world.get_picture()
                    self.droid.observe_world(pic)
                    choice = self.droid.make_choice(pic)
                    self.world.send_to_orig_world(choice)
                else:
                    pic = self.world.get_picture()
                    self.droid.record(pic, self.world.choice)
            tt = time.time() - t
            self.tick(tt)

    def main(self):
        keyboard.add_hotkey('Ctrl + Shift + Space', lambda: self.change_control())
        keyboard.add_hotkey('Ctrl + Alt + Space', lambda: self.deactivate())
        print("DROID: Loop started")
        self.loop()
