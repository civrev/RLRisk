"""
Minigame for playing with the full Risk mechanics
but on a smaller scale. The environment is restricted
to play on only the S. American and African continent
"""

import time
from rlrisk.environment import Risk
from rlrisk.minigames import SWGUI

class SouthernWarfare(Risk):
    """A minigame that is the full Risk game just for S. America and Africa"""

    def __init__(self, *args, **kwargs):
        """Constructor for SouthernWarfare that restricts the environment"""

        self.sleep_val = kwargs.pop('sleep_val', 0.5)

        super(SouthernWarfare, self).__init__(*args, **kwargs)

        if self.has_gui:
            self.gui = SWGUI()

        self.restrict_board()

        self.state = self.gen_init_state(len(self.board))

    def restrict_board(self):
        """
	Restricts board to S. America and Africa

	Removes references to all territories outside S. American
	or Africa from the game.

	Parameters
	----------
	None

	Returns
	-------
	None

	"""

        non_played_continents = list(self.continents.keys())
        non_played_continents.remove('S_America')
        non_played_continents.remove('Africa')
        for continent in non_played_continents:
            unplayed = self.continents[continent]
            for territory in unplayed:
                self.board.pop(territory, None)
            for territory in unplayed:
                for value in self.board.values():
                    if territory in value:
                        value.remove(territory)
            self.continents.pop(continent, None)

        fix = lambda x: x - 9
        for continent, provinces in self.continents.items():
            self.continents[continent] = [fix(terr) for terr in provinces]
        bad_keys = list(self.board.keys())
        good_keys = [fix(k) for k in bad_keys]

        for index, key in enumerate(bad_keys):
            self.board[good_keys[index]] = [fix(terr) for terr in self.board[key]]
            self.board.pop(key, None)

    def gui_update(self, verbose=False):
        super(SouthernWarfare, self).gui_update(verbose)

        if self.has_gui and self.verbose_gui:
            time.sleep(self.sleep_val)
