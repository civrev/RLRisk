'''
This class is the GUI for the minigame southern warfare
'''

from rlrisk.environment import GUI, Risk

class SWGUI(GUI):
    """GUI That only displays S. America and Africa"""

    def __init__(self):
        """Constructor for GUI but with un-needed area removed"""
        super(SWGUI, self).__init__()

        #filter out stuff we don't use in this minigame
        board, continents = Risk.gen_board()[:2]
        concerned = set(continents['Africa'] + continents['S_America'])
        to_pop = set(board) - concerned
        for position in to_pop:
            self.positions.pop(position)
        fix = lambda x: x - 9
        for key, value in list(self.positions.items()):
            self.positions[fix(key)] = value
            self.positions.pop(key, None)

        #crop screen
        left, top, right_offset, bottom_offset = (300, 250, 420, 350)
        self.background = self.background.subsurface((left, top, right_offset, bottom_offset))
        fix = lambda t: (t[0]-300, t[1]-250)
        for position in self.positions:
            self.positions[position] = fix(self.positions[position])
        self.init_draw()
