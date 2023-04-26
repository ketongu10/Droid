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
import DroidBase


class DroidNNW(DroidBase):
    def __init__(self):
        self.model = keras.Sequential([
                layers.Flatten(input_shape=(12, 12, 3)),
                #layers.LSTM(5),
                layers.Dense(16, activation="relu", name="layer1"),
                layers.Dense(5, name="output"), ])
        self.model.summary()
        loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        self.model.compile(optimizer='adam', loss=loss_fn, metrics=['accuracy'])

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
        r = tf.nn.softmax(self.model([picture]))
        #print(r, np.argmax(r.numpy()))

        #r = rnd.randint(0, 5)
        return tf.argmax(r[0])

    def record(self, picture):
        """Used to remember master's actions"""
        pass