import keyboard
import numpy as np
from Worlds.Snake import C
import pygame
import tensorflow as tf
import time
import random as rnd


class Droid:
    def __init__(self):
        pass

    def observe_world(self, picture):
        """Gets picture from World"""
        #print(picture.shape)
        pass

    def analyse(self):
        """Analyses master's actions, remembered earlier"""
        pass

    def make_choice(self):
        """Used to make a choice"""
        """ 0 - wait """
        """ 1 - up """
        """ 2 - right """
        """ 3 - down """
        """ 4 - left """

        r = rnd.randint(0, 5)
        return r

    def record(self, picture):
        """Used to remember master's actions"""
        pass


class World:
    """World used to communicate with the original World engine such as game or smth else"""
    def __init__(self, snake):
        self.original_world = snake.dis
        self.snake = snake
        self.fps = snake.snake_speed
        self.choice = 0

    def get_picture(self):
        """Gets picture from original World engine"""
        SH = C.snake_block
        display = self.original_world
        arr = np.zeros(((display.get_width() // SH), (display.get_height() // SH), 3), dtype=int)
        for i in range(display.get_width() // SH):
            for j in range(display.get_height() // SH):
                arr[i][j] = display.get_at([i * SH, j * SH])[:-1]

        return tf.convert_to_tensor(arr, dtype=tf.experimental.numpy.int8)

    def send_to_orig_world(self, choice):
        """Sends Droid's choice to the original World engine"""
        if choice is not None:
            if choice < 5:
                if choice == 1:
                    self.choice = pygame.K_UP
                elif choice == 2:
                    self.choice = pygame.K_RIGHT
                elif choice == 3:
                    self.choice = pygame.K_DOWN
                elif choice == 4:
                    self.choice = pygame.K_LEFT

            print(choice, self.choice)




class Server:
    """Server used to organise Droid and World communication"""
    def __init__(self, snake):
        self.world = World(snake)
        self.droid = Droid()
        self.guided = True
        self.is_active = True

    def tick(self, t):
        ticks = 1/self.world.fps - t
        #print(f'{1/t:.0f} fps')
        time.sleep(ticks if ticks > 0 else 0)

    def change_control(self):
        if self.guided:
            print("DROID: Master control activated")
            self.world.snake.snake_speed = C.snake_speed_slow
            self.guided = False
        else:
            print("DROID: Master control deactivated")
            self.guided = True
            self.world.snake.snake_speed = C.snake_speed_fast
            self.droid.analyse()

    def deactivate(self):
        print("DROID: Droid is deactivated")
        self.is_active = False
        self.guided = False

    def loop(self):
        self.guided = True
        self.is_active = True
        while self.is_active:
            t = time.time()
            if self.guided:
                pic = self.world.get_picture()
                self.droid.observe_world(pic)
                choice = self.droid.make_choice()
                self.world.send_to_orig_world(choice)
            else:
                pic = self.world.get_picture()
                self.droid.record(pic)
            t = time.time() - t
            self.tick(t)

    def main(self):
        keyboard.add_hotkey('Ctrl + Shift + Space', lambda: self.change_control())
        keyboard.add_hotkey('Ctrl + Alt + Space', lambda: self.deactivate())
        print("DROID: Loop started")
        self.loop()

