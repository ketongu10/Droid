"""
Created on July 3 2020
@author: Yigit GUNDUC
"""
#import pygame
import socket
import pickle
import cv2
from time import time
HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1244))
#pygame.init()
#sсreen = pygame.display.set_mode((1024, 1024))  # Создаем окно с разрешением 800x600
while True:
    full_msg = b''
    new_msg = True
    t0 = time()
    while True:
        msg = s.recv(1024) #32768)
        if new_msg:
            #print("new msg len:", msg[:HEADERSIZE])
            msglen = int(msg[:HEADERSIZE])
            new_msg = False

        #print(f"full message length: {msglen}")

        full_msg += msg

        print(len(full_msg))

        if len(full_msg)-HEADERSIZE == msglen:
            #print("full msg recvd")
            #print(full_msg[HEADERSIZE:])
            #x = pickle.loads(full_msg[HEADERSIZE:])
            #cv2.imwrite("recived.jpg", x)
            with open('image_received.jpg', 'wb') as f:
                f.write(full_msg[HEADERSIZE:])
            #received_img = pygame.image.frombytes(full_msg[HEADERSIZE:], (1024, 1024), "RGBA")
            #sсreen.blit(received_img, received_img.get_rect())
            new_msg = True
            full_msg = b''
            print(f"TIME={time()-t0}")
            break
        elif len(full_msg) - HEADERSIZE > msglen:
            break

