from rlrisk.environment import Risk
from rlrisk.minigames import SWGUI
from rlrisk.agents import BaseAgent

class SouthernWarfare(Risk):
    '''A minigame the uses the full Risk game just for S. America and Africa'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.gui = SWGUI()

if __name__=='__main__':
    players = [BaseAgent() for x in range(3)]
    env = SouthernWarfare(players)
    print(env.board)
