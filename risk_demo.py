'''
This program is to demonstrate the RLRisk package
is fully working after installation
'''

from rlrisk.environment import risk, gui
from rlrisk.agents.aggressive import AggressiveAgent
from rlrisk.agents.base_agent import BaseAgent
from rlrisk.agents.human import Human
import pandas as pd
import matplotlib.pyplot as plt


def plot_results(results):
    '''
    Plotting the results of a game into meaningful graphs
    '''
    #unpack results
    prov_r, troop_r, card_r, trade_r, steal_cards, turn_order = results

    p2c = gui.GUI.player_colors()
    roll = 20

    #plot number of owned territores by turn
    owner_df = pd.DataFrame(prov_r)
    owner_stats = [owner_df[owner_df==num].count(1).rolling(roll).mean() for num in range(len(players))]
    fig, ax = plt.subplots()
    for plr_num, plr in enumerate(owner_stats, 1):
        ax = plr.plot(ax=ax, kind='line', x='x', y='y', c=p2c[plr_num-1],label="Player "+str(plr_num))
    plt.legend(loc='best')
    plt.xlabel('Turn')
    plt.ylabel('Territories Controlled')
    plt.title('Territory Ownership By Player')
    plt.show()

    #plot number of troops by turn
    troop_df = pd.DataFrame(troop_r)
    troop_stats = [troop_df[owner_df==num].sum(1).rolling(roll).mean() for num in range(len(players))]
    fig, ax = plt.subplots()
    for plr_num, plr in enumerate(troop_stats, 1):
        ax = plr.plot(ax=ax, kind='line', x='x', y='y', c=p2c[plr_num-1],label="Player "+str(plr_num))
    plt.legend(loc='best')
    plt.xlabel('Turn')
    plt.ylabel('Total Troops')
    plt.title('Total Troop Count By Player')
    plt.show()

    #plot the ratio of troops to territories
    fig, ax = plt.subplots()
    for plr_num, trp_series in enumerate(troop_stats, 1):
        combo_series = trp_series / owner_stats[plr_num-1]
        ax = combo_series.plot(ax=ax, kind='line', x='x', y='y', c=p2c[plr_num-1],label="Player "+str(plr_num))
    plt.legend(loc='best')
    plt.xlabel('Turn')
    plt.ylabel('Average Troops / Owned Territory')
    plt.title('Troops/Territories Ratio By Player')
    plt.show()

#How to run a game using the normal rules
players = [BaseAgent() for x in range(5)]+[AggressiveAgent() for x in range(1)]
env = risk.Risk(players, has_gui=False)
results = env.play()

plot_results(results)






#---------------------------------------------------------------------------
#plotting
#---------------------------------------------------------------------------
#use the results of the game to plot meaningful informatio

