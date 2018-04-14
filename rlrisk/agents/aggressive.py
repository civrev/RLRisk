import random
import numpy as np
from rlrisk.agents import BaseAgent

class AggressiveAgent(BaseAgent):

    def take_action(self, state, action_code, options):
        
        #always risk maximum troops during attack
        if action_code == 3:
            return options[-1]

        #never retreat        
        if action_code == 2:
            return True

        #never pass on attack
        if action_code in [1,11] and len(options)>1:
            random.choice(options[:-1])

        #always sent troops to borders
        if action_code in [0,10,5,9]:
            if action_code==9:
                border_options = list(set(self.get_start_borders(state)).intersection(set(options)))
            else:
                border_options = list(set(self.get_borders(state)).intersection(set(options)))
            if len(border_options)!=0:
                return random.choice(border_options)

        #When fortifying, always choose destination
        if action_code == 6:
            return options[-1]

        #always move troops into newly conquered territory
        if action_code == 7:
            return options[-1]

        return random.choice(options)

    def get_borders(self, state):

        territories, cards, trade_ins = state

        owned = np.where(territories[:,0]==self.player)[0]

        borders = []
        for t in owned:
            links = self.board[t]
            for lt in links:
                if lt not in owned:
                    borders.append(t)
                    break

        return borders

    def get_start_borders(self, state):

        territories, cards, trade_ins = state
                
        owned = np.where(territories[:,0]==self.player)[0]

        borders = []
        for t in owned:
            links = self.board[t]
            for lt in links:
                if territories[lt,0]==-1:
                    borders.append(lt)

        return borders
