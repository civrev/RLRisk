"""
Minigame for replaying the first part of the game Risk
over and over again, when players choose their initial territories
"""

import time
from rlrisk.environment import Risk
from rlrisk.agents import BaseAgent
import numpy as np

class SPMinigame(Risk):
    '''Minigame for choosing initial territories before game start'''

    def __init__(self, agents, turn_order="c", has_gui=False,
                 fortify_adjacent=True, sleep_val=0.5):

        remove = False
        if not isinstance(agents, list):
            agents = [agents, BaseAgent()]
            remove = True

        super(SPMinigame, self).__init__(agents, turn_order, has_gui=has_gui,
                                         fortify_adjacent=fortify_adjacent)

        if remove:
            self.players = self.players[:1]
            self.turn_order = [0]

        self.sleep_val = sleep_val

    def play(self):
        """
	Begin Game

	Just a formality compared to parent class.
	Handles return objects and standardizes user interface

	Parameters
	----------
	None

	Returns
	-------
	(42, 42) Numpy Array :
	The pick-by-pick record of territory owners
	"""

        self.allocate_territories()
        return np.array(self.record[0])

    def allocate_territories(self):
        """
        Players choose territories

	Players are prompted to choose from the remaining territories
	one-by-one. When all territories are chosen the game terminates

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

            turn = self.turn_order[index % len(self.turn_order)]

            chosen = self.players[turn].take_action(self.state, 9, remaining)

            remaining.remove(chosen)

            territories[chosen, 0] = turn
            territories[chosen, 1] = 1

            self.state = (territories, cards, trade_ins)
            self.record[0].append(np.copy(self.state[0][:, 0]))

            self.gui_update()

        self.game_over = True
        self.gui_update()

    def gui_update(self, verbose=False):
        super(SPMinigame, self).gui_update(verbose)
        if self.has_gui:
            time.sleep(self.sleep_val)
