
import pygame.display
import matplotlib.pyplot as plt
import matplotlib
#matplotlib.use('module://pygame_matplotlib.backend_pygame')


class Renderer:
    def __init__(self):
        matplotlib.use('module://pygame_matplotlib.backend_pygame')
        fig, axes = plt.subplots(1, 1, figsize=(4, 2))
        self.fig = fig
        self.ax = axes
