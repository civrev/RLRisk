from rlrisk.environment import Risk
from rlrisk.agents import AggressiveAgent, BaseAgent
import numpy as np
import time
import random

class SPMinigame(Risk):
    def __init__(self, agents, turn_order="c", has_gui=False,
                 fortify_adjacent=True, sleep_val=0.5):
        '''Block Comment here'''

        remove = False
        if not isinstance(agents, list):
            agents = [agents, BaseAgent()]
            remove = True
        
        super().__init__(agents,turn_order,has_gui=has_gui,
                        fortify_adjacent=fortify_adjacent)

        if remove:
            self.players = self.players[:1]
            self.turn_order = [0]

        self.sleep_val = sleep_val
            

    def play(self):
        """
        Allocates territories to players at game start

        If rules are to randomly deal, assigns 1 troop to each player randomly
        in a territory going by turn order. Otherwise allows players to
        choose territories one by one

        Parameters
        ----------
        None
        
        Returns
        -------
        None

        """
        self.allocate_territories()
        self.gui.quit_game()
        return np.array(self.record[0])

    def allocate_territories(self):
        """
        Allocates territories to players at game start

        If rules are to randomly deal, assigns 1 troop to each player randomly
        in a territory going by turn order. Otherwise allows players to
        choose territories one by one

        Parameters
        ----------
        None
        
        Returns
        -------
        None

        """

        territories, cards, trade_ins = self.state

        remaining = list(range(42))

        for index in range(42):

            turn = self.turn_order[index%len(self.turn_order)]

            print('DEBUB Asked',9)
            chosen = self.players[turn].take_action(self.state, 9, remaining)

            remaining.remove(chosen)

            territories[chosen][0]=turn
            territories[chosen][1]=1

            self.state = (territories, cards, trade_ins)
            self.record[0].append(np.copy(self.state[0][:,0]))

            self.gui_update()

            if self.has_gui:
                time.sleep(self.sleep_val)
