from API.Droids.DroidBase import DroidBase
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression

import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
import random as rnd
BUFFERLENGTH = 1000
class DroidLinReg(DroidBase):

    def __init__(self, world):
        super().__init__(world)
        self.model = LogisticRegression(solver="liblinear")
        self.memory = np.zeros(shape=(BUFFERLENGTH, 12*12*3), dtype=int)
        self.choices = np.zeros(shape=(BUFFERLENGTH, ), dtype=int)
        self.feedback = np.zeros(shape=(BUFFERLENGTH, ), dtype=float)

        self.mem_load = 0
        self.is_studied = False
        print(f"SUM of memory: {self.memory.sum()}")

    def observe_world(self, picture):
        """Gets picture from World"""
        if not self.is_studied:
            if (self.mem_load < BUFFERLENGTH):
                self.memory[self.mem_load] = picture.numpy().reshape((432, ))
                self.choices[self.mem_load] = self.world.prev_choice
                self.feedback[self.mem_load] = self.world.prev_feedback
                self.mem_load += 1
                #print(f"FB: {self.world.prev_feedback}   CH: {self.world.prev_choice}")
            else:
                print(f"SUM of memory: {self.memory.sum()}")
                self.mem_load = 0
                self.analyse()
                self.is_studied = True

    def analyse(self):
        """Analyses master's actions, remembered earlier"""
        dataframe = np.ndarray(shape=(BUFFERLENGTH, 433), dtype=int)
        dataframe[:, :432] = self.memory
        dataframe[:, 432] = self.choices
        #print(self.memory.shape, self.feedback.shape)
        print(f"CONTROL SUM: {self.memory.sum()+self.choices.sum()} {dataframe.sum()}")
        self.model.fit(dataframe, self.feedback)

        print("DROID has analysed data. Score is: ", self.model.score(dataframe, self.feedback))
        print(f"FEEDBACK SUM is {self.feedback.sum()}")

    def make_choice(self, picture):
        """Used to make a choice"""
        """ 0 - wait """
        """ 1 - up """
        """ 2 - right """
        """ 3 - down """
        """ 4 - left """
        if self.is_studied:
            probs = []
            for choice in range(0, 5):
                data = np.ndarray(shape=(1, 433), dtype=int)
                data[:, :432] = picture.numpy().reshape((1, 432))
                data[:, 432] = choice
                probs.append(self.model.predict_proba(data)[0][1])
                """if self.model.predict_proba(data)[0][1] > 0.75:
                    print(" > 1 PREDICT and CHOICE", self.model.predict(data), choice)
                    return choice
                elif self.model.predict_proba(data)[0][1] > 0.75:
                    print(" > 0 PREDICT and CHOICE", self.model.predict(data), choice)
                    return choice
                else:
                    print("PREDICT and CHOICE", self.model.predict(data), choice)
                    r = super().make_choice(picture)"""
            ind = np.argmax(probs)
            print(ind, probs[ind])
            return ind
        else:
            r = super().make_choice(picture)
        return r

    def record(self, picture, right_choice):
        """Used to remember master's actions"""
        pass
        if not self.is_studied:
            if (self.mem_load < BUFFERLENGTH):
                self.memory[self.mem_load] = picture.numpy().reshape((432,))
                self.feedback[self.mem_load] = rnd.randint(0, 5)
                self.mem_load += 1
                print(f"DROID IS WATCHING. CURRENT BUFFER IS: {self.mem_load}")
            else:
                print(f"SUM of memory: {self.memory.sum()}")
                self.mem_load = 0
                self.analyse()
                self.is_studied = True
