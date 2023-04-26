import keyboard
import numpy as np
from Worlds.Snake import C
import pygame
import tensorflow as tf
import time
import random as rnd
import tensorflow as tf
from tensorflow import keras
from keras import layers
from keras import models


class DroidBase:

    def __init__(self, world):
        self.model = None
        self.world = world


    def observe_world(self, picture):
        """Gets picture from World"""
        pass

    def analyse(self):
        """Analyses master's actions, remembered earlier"""
        pass

    def make_choice(self, picture):
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