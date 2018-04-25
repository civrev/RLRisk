'''
rlrisk.minigames
================

A subpackage for environments that represent some part
of the full Risk game enviroment

Available Modules
-----------------
pick_start_positions
    A minigame for replaying territory allocation over and over again

southern_gui
    GUI for SouthernWarfare minigame

southern_warfare
    A minigame that is the full Risk environment mechanics
    restricted to just S. American and Africa
'''

from .pick_start_positions import SPMinigame
from .southern_gui import SWGUI
from .southern_warfare import SouthernWarfare

__all__ = ['SPMinigame', 'SWGUI', 'SouthernWarfare']
