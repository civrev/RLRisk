import rlrisk as rlr
from rlrisk.minigames.southern_gui import SGUI

class SouthernWarfare(object):
    '''A minigame the uses the full Risk game just for S. America and Africa'''

    def __init__(self, agents):
        '''sets up minigame'''
        self.gui = SGUI()
        self.board, self.continents, cf = rlr.environment.risk.Risk.gen_board()
        self.state = rlr.environment.risk.Risk.gen_init_state(False, [0])
