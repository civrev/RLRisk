'''
rlrisk.environment
==================

Available Modules
-----------------
config
    Functions for configuring game settings

gui
    GUI for observing game environment

risk
    Environment for Risk board game
'''

from .gui import GUI
from .risk import Risk

__all__ = ['GUI', 'Risk']
