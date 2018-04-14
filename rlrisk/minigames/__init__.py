'''
A reinforcement learning environment based off the board game Risk

https://github.com/civrev/RLRisk

by Christian Watts
'''

from .pick_start_positions import SPMinigame
from .southern_gui import SWGUI
from .southern_warfare import SouthernWarfare

__all__ = ['SPMinigame', 'SWGUI', 'SouthernWarfare']
