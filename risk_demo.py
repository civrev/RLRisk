'''
This program is to demonstrate the RLRisk package
is fully working after installation
'''

from rlrisk.environment import Risk, GUI
from rlrisk.agents import BaseAgent, AggressiveAgent, Human
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools

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

def custom_gen():
    num=1
    while True:
        num += 1+int(num*0.1)
        yield num

#Main
if __name__ == '__main__':
    #Play the game
    players = [AggressiveAgent() for x in range(6)]
    env = Risk(players, has_gui=True, turn_cap=1000)
    results = env.play()

    trade_gen = env.gen_backup
    plot_results(results, players, trade_gen,5)
