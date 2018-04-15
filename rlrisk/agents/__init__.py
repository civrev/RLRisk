'''
A reinforcement learning environment based off the board game Risk

https://github.com/civrev/RLRisk

by Christian Watts
'''

from .base_agent import BaseAgent
from .aggressive import AggressiveAgent
from .human import Human

__all__ = ['BaseAgent', 'AggressiveAgent', 'Human']
