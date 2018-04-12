#risk.py
#Christian Watts

import sys
import random
import os
import pygame
import numpy as np
import pandas as pd
from rlrisk.environment import  config, gui
from rlrisk.environment.risk import Risk
from rlrisk.agents.base_agent import BaseAgent
from rlrisk.agents.human import Human
from rlrisk.minigames.pick_start_positions import PickStartGame
from rlrisk.minigames.southern_warfare import SouthernWarfare



    

#****************************************************************
menu = {}

stop = True
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
