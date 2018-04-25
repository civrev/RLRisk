#risk.py
#Christian Watts

import sys
import random
import os
import pygame
from position_minigame_agent import StartLearningAgent
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import keras
from rlrisk.environment import *
from rlrisk.agents import *
from rlrisk.minigames import *

def plot_results(results, players, trade_gen, roll=20, lw=2):
    '''
    Plotting the results of a game into meaningful graphs
    '''
    #unpack results
    prov_r, troop_r, card_r, trade_r, steal_cards, turn_order = results

    p2c = GUI.player_colors()

    #plot number of owned territores by turn
    owner_df = pd.DataFrame(prov_r)
    owner_stats = [owner_df[owner_df==num].count(1).rolling(roll).mean() for num in range(len(players))]
    fig, ax = plt.subplots()
    for plr_num, plr in enumerate(owner_stats, 1):
        ax = plr.plot(ax=ax, kind='line', x='x', y='y', c=p2c[plr_num-1],label="Player "+str(plr_num),linewidth=lw)
    plt.legend(loc='best')
    plt.xlabel('Turn')
    plt.ylabel('Territories Controlled')
    plt.title('Territory Ownership By Player')

    #plot number of troops by turn
    troop_df = pd.DataFrame(troop_r)
    troop_stats = [troop_df[owner_df==num].sum(1).rolling(roll).mean() for num in range(len(players))]
    fig, ax = plt.subplots()
    for plr_num, plr in enumerate(troop_stats, 1):
        ax = plr.plot(ax=ax, kind='line', x='x', y='y', c=p2c[plr_num-1],label="Player "+str(plr_num),linewidth=lw)

    trade_values = [next(trade_gen) for num in range(trade_r[-1]+1)]
    trade_rv = np.array([trade_values[x] for x in trade_r])
    plt.plot(trade_rv, label='Value of Set Trade In', color='blue', linestyle='--', linewidth=lw)
    
    plt.legend(loc='best')
    plt.xlabel('Turn')
    plt.ylabel('Total Troops')
    plt.title('Total Troop Count By Player')

    plt.show()

def multi_game():

    players = [AggressiveAgent() for x in range(6)]
    ui = int(input("How many games? "))
    length=[]
    for x in range(ui):
        length.append(Risk(players).play()[0].shape[0])
    print('Done! Average game is ',sum(length)/len(length),'turns')

def full_demo():
    players = [AggressiveAgent() for x in range(6)]
    env = Risk(players, has_gui=True)
    results = env.play()
    trade_gen = env.gen_backup
    plot_results(results, env.players, trade_gen, 5)

def start_mg():
    players = [AggressiveAgent() for x in range(6)]
    ui = int(input("How many games? "))
    gui = int(input("With gui? 0/1 "))
    sv=0
    if gui>0:
        sv = 0.2
    for x in range(ui):
        SPMinigame(players, has_gui=gui, sleep_val=sv).play()
    print('Done!',ui,'Minigames where played!')

def sw_demo():
    players = [AggressiveAgent() for x in range(6)]
    env = SouthernWarfare(players, has_gui=True, verbose_gui=True, turn_cap=1000, sleep_val=0.03)
    results = env.play()
    plot_results(results, env.players, env.gen_backup, 1)

def sw_minigame():
    players = [AggressiveAgent() for x in range(6)]
    ui = int(input("How many games? "))
    gui = int(input("With gui? 0/1 "))
    for x in range(ui):
        SouthernWarfare(players, has_gui=gui, turn_cap=1000).play()
    print('Done!',ui,'Minigames where played!')

def nn_demo():
    nnp = StartLearningAgent()
    try:
        nnp.model = keras.models.load_model('101_turns.h5')
    except:
        print("model not loaded")
    players = [nnp]+[BaseAgent()]#+[AggressiveAgent()]
    ui = int(input("How many games? "))
    f_list = []
    for x in range(ui):
        if x % 10 == 0:
            gui = True
            print(x,'F Mean:',sum(f_list[-5:])/5)
            nnp.epsilon = 0
        else:
            gui = False
            nnp.epsilon = 0.05
        nnp.v_flag=gui
        env = SPMinigame(nnp, has_gui=gui, sleep_val=0.2)
        env.play()
        f_list.append(nnp.prev_reward)
        nnp.update()
        nnp.reset()
    
    nnp.model.save(str(ui)+'_turns.h5')

#****************************************************************
menu = {'1: Play Multiple Aggressive Games':multi_game,
        '2: Play Starting Positions Minigame':start_mg,
        '3: Play Southern Warfare Minigame':sw_minigame,
        '4: Play full Risk demo':full_demo,
        '5: Play SouthernWarfare Demo':sw_demo,
        '6: Play Starting Position Minigame with NN Agent':nn_demo}

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
