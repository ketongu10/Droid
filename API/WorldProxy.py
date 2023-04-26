
import numpy as np
from Worlds.Snake import C
import pygame
import tensorflow as tf


class WorldProxy:
    """World used to communicate with the original World engine such as game or smth else"""
    def __init__(self, snake):
        self.original_world = snake.dis
        self.snake = snake
        self.fps = snake.snake_speed
        self.feedback = 0   # 0 if snake is dead, 2 if snake ate apple
        self.choice = 0
        self.choiceINT = 0
        self.prev_choice = 0
        self.prev_feedback = 0

    def get_picture(self):
        """Gets picture from original World engine"""
        SH = C.snake_block
        display = self.original_world
        arr = np.zeros(((display.get_width() // SH), (display.get_height() // SH), 3), dtype=int)
        for i in range(display.get_width() // SH):
            for j in range(display.get_height() // SH):
                arr[i][j] = display.get_at([i * SH, j * SH])[:-1]
        return tf.convert_to_tensor([arr], dtype=tf.int32)#tf.experimental.numpy.int8)

    def send_to_orig_world(self, choice):
        """Sends Droid's choice to the original World engine"""
        if choice is not None:
            if choice < 5:
                if choice == 1:
                    self.choice = pygame.K_UP
                    self.prev_choice, self.choiceINT = self.choiceINT, choice
                elif choice == 2:
                    self.choice = pygame.K_RIGHT
                    self.prev_choice, self.choiceINT = self.choiceINT, choice
                elif choice == 3:
                    self.choice = pygame.K_DOWN
                    self.prev_choice, self.choiceINT = self.choiceINT, choice
                elif choice == 4:
                    self.choice = pygame.K_LEFT
                    self.prev_choice, self.choiceINT = self.choiceINT, choice

            #print(choice, self.choice)
