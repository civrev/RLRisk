from rlrisk.environment import Risk
from rlrisk.agents import BaseAgent
from rlrisk.minigames import SWGUI
import numpy as np

class SouthernWarfare(Risk):
    '''A minigame the uses the full Risk game just for S. America and Africa'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

        if self.has_gui:
            self.gui = SWGUI()

        self.restrict_board()

    def restrict_board(self):
        '''bc'''

        non_played_continents = list(self.continents.keys())
        non_played_continents.remove('S_America')
        non_played_continents.remove('Africa')
        for c in non_played_continents:
            unplayed = self.continents[c]
            for territory in unplayed:
                self.board.pop(territory,None)
            for territory in unplayed:
                for key,value in self.board.items():
                    try:
                        value.remove(territory)
                    except:
                        pass
            self.continents.pop(c,None)

        fix = lambda x: x-9
        for c,provinces in self.continents.items():
            self.continents[c]=[fix(t) for t in provinces]
        for t,links in self.board.items():
            self.board[fix(t)]=[fix(link) for link in links]
            self.board.pop(t, None)

    @staticmethod
    def gen_init_state():
        territory = np.array([-1, 0])
        territories = np.array([territory for x in range(10)])
        cards = np.repeat(6, 44)
        return (territories, cards, 0)
