#risk.py
#Christian Watts

import sys
import random
import os
import pygame
import numpy as np
import pandas as pd
from rlrisk.environment import *
from rlrisk.agents import *
from rlrisk.minigames import *


def multi_game():

    players = [AggressiveAgent() for x in range(6)]
    ui = int(input("How many games? "))
    length=[]
    for x in range(ui):
        length.append(Risk(players).play()[0].shape[0])
    print('Done! Average game is ',sum(length)/len(length),'turns')
    

#****************************************************************
menu = {'1: Play Multiple Aggressive Games':multi_game}

stop = False
while not stop:
    [print(x) for x in sorted(list(menu.keys()))]
    print('-1 for quit')
    user=0
    try:
        user=int(input("Make a selection: "))
    except:
        print("you MUST input a number")
    if user in range(1,len(menu)+1):
        menu[sorted(list(menu.keys()))[user-1]]()
    elif user==0:
        continue
    else:
        stop=True
