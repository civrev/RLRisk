'''
RLRisk
======

A reinforcement learning environment based off the board game Risk

Provides
    1. A quick and familiar environment for playing the game Risk
    2. Customizable game settings from popular rulesets
    3. An easy way to explore agent performace

Playing a game of RLRisk is as easy as::

    >>> from rlrisk.agents import *
    >>> from rlrisk.environment import *
    >>> players = [BaseAgent(), AggressiveAgent()]
    >>> env = Risk(players)
    >>> results = env.play()

Available Subpackages
---------------------
agents
    Agents that interact with the environment

environment
    Core game environment and GUI

minigames
    Smaller versions of the full game that focus on
    specific aspects of gameplay and learning
'''
