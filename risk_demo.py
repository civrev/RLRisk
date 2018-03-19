'''
This program is to demonstrate the RLRisk package
is fully working after installation
'''

from rlrisk.environment import risk
from rlrisk.agents.base_agent import BaseAgent
from rlrisk.agents.human import Human

# generate 6 players, one of them human
# players must be initialized with a player #
# ie player 0->5 for 6 players
players = [Human(0)]+[BaseAgent(x) for x in range(1,6)]

# create a game of Risk using standard ruleset
# must include a list of players
env = risk.standard_game(players)

# begin game
# by defualt the game has the GUI set to False
env.play()
