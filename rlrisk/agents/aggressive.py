"""
A module that holds a class for an agent that always makes
"aggressive" choices. Useful for making the game end faster
"""

import random
import numpy as np
from rlrisk.agents import BaseAgent

class AggressiveAgent(BaseAgent):
    """An aggressive random agent"""

    def take_action(self, state, action_code, options):
        """
        Always make that aggressive move.

        Overview of aggressive behavior:
            always risk maximum troops during attack
            never retreat
            never pass on attack
            always sent troops to borders
            always fortify towards borders
            always move troops into newly conquered territory

        """

        #always risk maximum troops during attack
        if action_code == 3:
            return options[-1]

        #never retreat
        if action_code == 2:
            return True

        #never pass on attack
        if action_code in [1, 11] and len(options) > 1:
            random.choice(options[:-1])

        #always sent troops to borders
        if action_code in [0, 10, 5, 9]:
            if action_code == 9:
                border_options = list(set(self.get_start_borders(state)).intersection(set(options)))
            else:
                border_options = list(set(self.get_borders(state)).intersection(set(options)))
            if len(border_options) != 0:
                return random.choice(border_options)

        #When fortifying, always choose destination
        if action_code == 6:
            return options[-1]

        #always move troops into newly conquered territory
        if action_code == 7:
            return options[-1]

        return random.choice(options)

    def get_borders(self, state):
        """
        Get territories bordering this player's owned territories

        Calculates territories adjacent to player owned territories

        Required Parameters
        -------------------
        state : 3 value tuple
            (42, 2) Numpy Array : Indexed by territory ID, the first colum
                is player owner, and the second one is the number of troops
                in that territory

            (44,) Numpy Array : The status of all cards in the deck, either
                the player number for ownership by that player or 6 representing
                unowned

            integer : The number or card sets traded in so far

        Returns
        -------
        list : Territory IDs of border territories
        """

        territories = state[0]

        owned = np.where(territories[:, 0] == self.player)[0]

        borders = []
        for terr in owned:
            links = self.board[terr]
            for link in links:
                if link not in owned:
                    borders.append(terr)
                    break

        return borders

    def get_start_borders(self, state):
        """
        Get internal player territory borders

        Calculates owned territories that are on the outskirts
        of contiguously owned territory

        Required Parameters
        -------------------
        state : 3 value tuple
            (42, 2) Numpy Array : Indexed by territory ID, the first colum
                is player owner, and the second one is the number of troops
                in that territory

            (44,) Numpy Array : The status of all cards in the deck, either
                the player number for ownership by that player or 6 representing
                unowned

            integer : The number or card sets traded in so far

        Returns
        -------
        list : Territory IDs of border territories
        """

        territories = state[0]

        owned = np.where(territories[:, 0] == self.player)[0]

        borders = []
        for terr in owned:
            links = self.board[terr]
            for link in links:
                if territories[link, 0] == -1:
                    borders.append(link)

        return borders
