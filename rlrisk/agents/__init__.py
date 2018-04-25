'''
rlrisk.agents
=============

Predefined agents for interacting with the game environment

Available Modules
-----------------
aggressive
    An agent that makes "aggressive" choices wherever possible. Useful for
    needing random agents that move towards the end of the game

base_agent
    An agent that is the parent of all other agents. Makes random choices

human
    An agent that request user input and validates it for an action
    to perform
'''

from .base_agent import BaseAgent
from .aggressive import AggressiveAgent
from .human import Human

__all__ = ['BaseAgent', 'AggressiveAgent', 'Human']
